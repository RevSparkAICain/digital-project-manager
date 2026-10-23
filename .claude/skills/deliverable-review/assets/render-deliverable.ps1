<#
.SYNOPSIS
    Turns an Office deliverable (deck, Word file or workbook) into images a reviewer can open.

.DESCRIPTION
    Windows only. Requires Windows PowerShell 5.1 (the worker is relaunched with whatever
    PowerShell executable started the script), Microsoft Office registered for COM, and, for
    Word files and workbooks, `python` or the `py` launcher on PATH with PyMuPDF installed.

    Call it inside the current session with the call operator. Do not add an execution
    policy override:

        & "assets/render-deliverable.ps1" -In "<file>" -Out "<scratch-dir>" [-TimeoutSec 180] [-NoPng] [-Dpi 100]

    Switches
        -In          the deliverable: .pptx .ppt .docx .doc .xlsx or .xls
        -Out         scratch folder for the results; created when missing; may not be the
                     folder the deliverable sits in
        -TimeoutSec  seconds the Office worker may run before it is stopped (180)
        -NoPng       Word files and workbooks stop at the PDF; decks ignore it
        -Dpi         page-image resolution for Word files and workbooks (100); decks ignore it
    -Worker and -PidFile are internal. The script passes them when it relaunches itself.

    What lands in -Out
        Every name starts with a stem: the letter r and eight hex digits cut from a SHA-256
        of the lowercased full input path. The deliverable's own name never appears, which
        keeps output paths short and stable for a given document.
        deck            <stem>\Slide1.PNG, Slide2.PNG, ... each 1280x720
        Word, workbook  <stem>.pdf with <stem>-p01.png, <stem>-p02.png, ... (one per page)
    The first output line maps the stem back to the deliverable's name. Output travels on
    the success stream and failures on the error stream, so a caller can capture either.

    Exit codes
        0      artifacts are on disk and the worker reported success
        1      refused up front: no such input, an unsupported type, or -Out is the
               input's own folder
        2      the worker ran past -TimeoutSec and was stopped
        3      the worker ended and nothing was produced
        4      artifacts exist but the worker never reported success
        5      the PDF exists but the page images failed
        6      the page images do not match the PDF's page total, or the total could not
               be read
        7      the longest output path would pass 259 characters; nothing was started
        other  the worker failed with that code
    Any non-zero code means the deliverable is UNREVIEWED.

    Path ceiling
        Long paths are assumed to be switched off, so MAX_PATH is 260 characters including
        the closing null, leaving 259 usable. PyMuPDF cannot save a PNG at 260 even though
        .NET can write one, so the guard sits at 259 and fires before any Office work.
        Word COM ignores the \\?\ extended prefix, so there is no way around the ceiling at
        render time; a shorter -Out is the only fix.

    Office safety
        The worker lists the running processes of the Office image just before it creates
        the application and again just after. The render owns the instance only when
        exactly one new process shows up between the two lists. That one ID and its start
        time go to the PID file at once; the instance is quit at the end and force-ended by
        process ID only if it outlives Quit by ten seconds. A process whose start time
        cannot be read is never force-ended, and a recorded ID that now names another
        program, or a process younger than the recorded start, has been reused and is left
        alone. With no new process, or with two or more (someone opened the same app in that
        moment), no ID is recorded and the instance is treated as the operator's: the script
        changes none of its settings, opens the file read-only, closes only that file, never
        quits it, and leaves it running. No Office process is ever ended by image name.

    Hangs
        A stalled render is nearly always a dialog inside a shared Office instance. Close that
        Office application yourself and run again, or raise -TimeoutSec. On a timeout the
        script ends only the processes recorded in the PID file.
#>
[CmdletBinding()]
param(
    [Parameter(Mandatory)]
    [string]$In,

    [Parameter(Mandatory)]
    [string]$Out,

    [int]$TimeoutSec = 180,

    [switch]$NoPng,

    [int]$Dpi = 100,

    [switch]$Worker,

    [string]$PidFile
)

# ---------------------------------------------------------------- shared setup ---

try { [Console]::OutputEncoding = New-Object System.Text.UTF8Encoding($false) } catch { }
$ErrorActionPreference = 'Stop'

$script:UsablePathLimit = 259
$script:KnownTypes = @('.pptx', '.ppt', '.docx', '.doc', '.xlsx', '.xls')
$script:DeckTypes = @('.pptx', '.ppt')
$script:OfficeImages = @('WINWORD', 'POWERPNT', 'EXCEL')

function Get-PidsByImage([string]$Image) {
    $ids = @(Get-Process -Name $Image -ErrorAction SilentlyContinue | ForEach-Object { $_.Id })
    return , $ids
}

function Get-StartTicks([int]$Id) {
    try {
        return [long](Get-Process -Id $Id -ErrorAction Stop).StartTime.ToUniversalTime().Ticks
    } catch {
        return [long]0
    }
}

# Answers 'gone', 'reused', 'unproven' or 'alive' for a process ID this render recorded as
# its own. 'reused' covers an ID that now belongs to something other than Word, PowerPoint
# or Excel, a process younger than the recorded start time, or one whose start time cannot
# be read now. 'unproven' is a running Office process whose start time was never recorded
# (0 or below): nothing proves it is the one this render started. Only 'alive' may be
# force-ended.
function Get-OwnedProcessState([int]$Id, [long]$RecordedTicks) {
    $proc = Get-Process -Id $Id -ErrorAction SilentlyContinue
    if ($null -eq $proc) { return 'gone' }
    if ($script:OfficeImages -notcontains $proc.ProcessName.ToUpperInvariant()) { return 'reused' }
    if ($RecordedTicks -le 0) { return 'unproven' }
    try {
        $nowTicks = $proc.StartTime.ToUniversalTime().Ticks
    } catch {
        return 'reused'
    }
    if ($nowTicks -gt $RecordedTicks) { return 'reused' }
    return 'alive'
}

# Returns the one process ID that is in -After but not in -Before. With no new ID, or with
# more than one, it returns nothing: a process the operator opened at the same moment cannot
# be told apart from the one this render created, so neither is claimed.
function Select-OwnedPid([int[]]$Before, [int[]]$After) {
    $added = @($After | Where-Object { $Before -notcontains $_ } | Select-Object -Unique)
    if ($added.Count -eq 1) {
        return [int]$added[0]
    }
}

function Get-RenderStem([string]$FullPath) {
    $hasher = [System.Security.Cryptography.SHA256]::Create()
    try {
        $digest = $hasher.ComputeHash([System.Text.Encoding]::UTF8.GetBytes($FullPath.ToLowerInvariant()))
    } finally {
        $hasher.Dispose()
    }
    $hex = -join ($digest[0..3] | ForEach-Object { $_.ToString('x2') })
    return 'r' + $hex
}

function Get-WorstCasePath([string]$Folder, [string]$Stem, [bool]$IsDeck) {
    if ($IsDeck) {
        return [System.IO.Path]::Combine($Folder, $Stem, 'Slide999.PNG')
    }
    return [System.IO.Path]::Combine($Folder, $Stem + '-p99.png')
}

function Test-IsPageImage([string]$FileName, [string]$Stem) {
    return ($FileName -like ($Stem + '-p*.png'))
}

function Remove-Quietly([string]$Path) {
    try {
        if ([System.IO.File]::Exists($Path)) { [System.IO.File]::Delete($Path) }
    } catch { }
}

# ------------------------------------------------------------------ worker mode ---

# The worker's stdout is a file the parent reads after the child ends, so worker log lines
# are written to the console writer directly and can never leak into a return value.
function Write-Line([string]$Text) {
    [Console]::Out.WriteLine($Text)
}

function Write-WorkerFailure([string]$Text) {
    [Console]::Error.WriteLine($Text)
}

# Brings up an Office application and decides whether this render owns it. Ownership needs
# exactly one process ID that was absent a moment before creation (Select-OwnedPid). That
# ID, with its start time, is appended to the PID file straight away; should the worker
# freeze later, the parent still knows exactly which process it may end. Anything else
# counts as attached: no ID is recorded, and the instance is never quit or force-ended.
# If a step after creation fails, the link goes through Disconnect-OfficeApp, so an owned
# instance gets the same Quit, ten-second wait and guarded stop as a normal teardown.
function Connect-OfficeApp([string]$ClassName, [string]$Image, [string]$Label) {
    $priorPids = Get-PidsByImage $Image
    $com = New-Object -ComObject $ClassName
    $link = [pscustomobject]@{
        Com    = $com
        Ours   = $false
        Pids   = @()
        Starts = @{}
        Label  = $Label
    }
    try {
        Start-Sleep -Milliseconds 400
        $currentPids = Get-PidsByImage $Image
        $ownedPid = Select-OwnedPid -Before $priorPids -After $currentPids

        if ($null -ne $ownedPid) {
            $ticks = Get-StartTicks $ownedPid
            $link.Ours = $true
            $link.Pids = @($ownedPid)
            $link.Starts[$ownedPid] = $ticks
            if ($PidFile) {
                $entry = @([string]$ownedPid)
                if ($ticks -gt 0) { $entry += ('start:{0}:{1}' -f $ownedPid, $ticks) }
                Add-Content -LiteralPath $PidFile -Value $entry -Encoding Ascii
            }
            Write-Line ('guard: started a new {0} instance (PID {1}); the render will quit it when done.' -f $Label, $ownedPid)
        } else {
            Write-Line ('guard: attached to an already running {0} instance (PID {1}). It will not be quit, none of its settings will change, and the file opens read-only. If the render hangs, close {0} yourself and run again.' -f $Label, ($currentPids -join ', '))
        }
    } catch {
        try { Disconnect-OfficeApp $link } catch { Write-Line ('cleanup: teardown failed: ' + $_.Exception.Message) }
        throw
    }

    return $link
}

function Disconnect-OfficeApp($Link) {
    if ($null -eq $Link) { return }

    if ($Link.Ours) {
        try {
            [void]$Link.Com.Quit()
        } catch {
            Write-Line ('cleanup: {0} raised an error on Quit: {1}' -f $Link.Label, $_.Exception.Message)
        }
    } else {
        Write-Line ('cleanup: {0} belongs to the operator, so Quit is skipped.' -f $Link.Label)
    }

    try { [void][System.Runtime.InteropServices.Marshal]::ReleaseComObject($Link.Com) } catch { }
    $Link.Com = $null
    [GC]::Collect()
    [GC]::WaitForPendingFinalizers()
    [GC]::Collect()

    if (-not $Link.Ours) { return }

    foreach ($id in $Link.Pids) {
        $recordedTicks = [long]0
        if ($Link.Starts.ContainsKey([int]$id)) { $recordedTicks = [long]$Link.Starts[[int]$id] }
        $giveUpAt = [DateTime]::UtcNow.AddSeconds(10)
        $state = Get-OwnedProcessState $id $recordedTicks
        while (($state -eq 'alive' -or $state -eq 'unproven') -and [DateTime]::UtcNow -lt $giveUpAt) {
            Start-Sleep -Milliseconds 250
            $state = Get-OwnedProcessState $id $recordedTicks
        }
        if ($state -eq 'alive') {
            # Forcing is allowed here only because this render launched the process and its
            # recorded start time still matches.
            try {
                Stop-Process -Id $id -Force -ErrorAction Stop
                Write-Line ('cleanup: {0} PID {1} was still alive 10 s after Quit and was force-ended.' -f $Link.Label, $id)
            } catch {
                Write-Line ('cleanup: {0} PID {1} survived Quit and could not be ended: {2}' -f $Link.Label, $id, $_.Exception.Message)
            }
        } elseif ($state -eq 'unproven') {
            Write-Line ('cleanup: {0} PID {1} outlived Quit, but its start time was never recorded, so it is left running.' -f $Link.Label, $id)
        } elseif ($state -eq 'reused') {
            Write-Line ('cleanup: {0} PID {1} now names another process (reused, left alone).' -f $Link.Label, $id)
        } else {
            Write-Line ('cleanup: {0} PID {1} exited cleanly.' -f $Link.Label, $id)
        }
    }
}

function Release-ComHandle($Handle) {
    if ($null -ne $Handle) {
        try { [void][System.Runtime.InteropServices.Marshal]::ReleaseComObject($Handle) } catch { }
    }
}

function Clear-OldScratch {
    $oldest = [DateTime]::Now.AddDays(-1)
    $candidates = @()
    try { $candidates = [System.IO.Directory]::GetFiles($env:TEMP, 'dlrv_*') } catch { return }
    foreach ($candidate in $candidates) {
        if (-not ([System.IO.Path]::GetFileName($candidate) -like 'dlrv_*')) { continue }
        try {
            if ([System.IO.File]::GetLastWriteTime($candidate) -lt $oldest) {
                [System.IO.File]::Delete($candidate)
            }
        } catch { }
    }
}

function Export-Deck([string]$Source, [string]$Target) {
    $link = $null
    $deck = $null
    try {
        $link = Connect-OfficeApp 'PowerPoint.Application' 'POWERPNT' 'PowerPoint'
        if ($link.Ours) {
            $link.Com.DisplayAlerts = 1
        }
        # msoTrue is -1 and msoFalse is 0: open read-only and untitled, with no window.
        $deck = $link.Com.Presentations.Open($Source, -1, -1, 0)
        [void][System.IO.Directory]::CreateDirectory($Target)
        [void]$deck.Export($Target, 'PNG', 1280, 720)
        $made = @(Get-ChildItem -LiteralPath $Target -Filter 'Slide*.PNG' -File).Count
        if (-not $made) {
            throw "PowerPoint completed the export without writing a single slide image to $Target"
        }
        Write-Line ('deck: {0} slide image(s) written to {1}' -f $made, $Target)
    } finally {
        if ($null -ne $deck) {
            try { [void]$deck.Close() } catch { }
            Release-ComHandle $deck
            $deck = $null
        }
        try { Disconnect-OfficeApp $link } catch { Write-Line ('cleanup: teardown failed: ' + $_.Exception.Message) }
    }
}

function Export-WordFile([string]$Source, [string]$Extension, [string]$PdfPath) {
    $link = $null
    $doc = $null
    # Word opens a local copy, so a network or redirected source cannot stall COM.
    $localCopy = Join-Path $env:TEMP ('dlrv_' + [guid]::NewGuid().ToString('N') + $Extension)
    try {
        Copy-Item -LiteralPath $Source -Destination $localCopy
        $link = Connect-OfficeApp 'Word.Application' 'WINWORD' 'Word'
        if ($link.Ours) {
            $link.Com.Visible = $false
            $link.Com.DisplayAlerts = 0
            $link.Com.AutomationSecurity = 3
        }
        # Keep both calls short. Spelling out every optional export argument can leave a
        # hidden Word spinning at full CPU with no way out.
        $doc = $link.Com.Documents.Open($localCopy, $false, $true)
        [void]$doc.ExportAsFixedFormat([string]$PdfPath, 17)
        if (-not (Test-Path -LiteralPath $PdfPath)) {
            throw "Word finished the export but no PDF exists at $PdfPath"
        }
        Write-Line ('document: PDF written to ' + $PdfPath)
    } finally {
        if ($null -ne $doc) {
            try { [void]$doc.Close(0) } catch { }
            Release-ComHandle $doc
            $doc = $null
        }
        try { Disconnect-OfficeApp $link } catch { Write-Line ('cleanup: teardown failed: ' + $_.Exception.Message) }
        try {
            if ([System.IO.File]::Exists($localCopy)) { [System.IO.File]::Delete($localCopy) }
        } catch {
            Write-Line ('cleanup: could not delete the temporary copy ' + $localCopy + ': ' + $_.Exception.Message)
        }
    }
}

function Export-Workbook([string]$Source, [string]$PdfPath) {
    $link = $null
    $book = $null
    try {
        $link = Connect-OfficeApp 'Excel.Application' 'EXCEL' 'Excel'
        if ($link.Ours) {
            $link.Com.Visible = $false
            $link.Com.DisplayAlerts = $false
            $link.Com.AskToUpdateLinks = $false
        }
        # Second argument 0 leaves external links stale; the third opens without write access.
        $book = $link.Com.Workbooks.Open($Source, 0, $true)
        [void]$book.ExportAsFixedFormat(0, [string]$PdfPath)
        if (-not (Test-Path -LiteralPath $PdfPath)) {
            throw "Excel finished the export but no PDF exists at $PdfPath"
        }
        Write-Line ('workbook: PDF written to ' + $PdfPath)
    } finally {
        if ($null -ne $book) {
            try { [void]$book.Close($false) } catch { }
            Release-ComHandle $book
            $book = $null
        }
        try { Disconnect-OfficeApp $link } catch { Write-Line ('cleanup: teardown failed: ' + $_.Exception.Message) }
    }
}

$script:RasterizerSource = @'
import os
import sys


def rasterize(argv):
    try:
        import fitz
    except ImportError:
        print("PyMuPDF is missing (module fitz); install it with: pip install pymupdf", file=sys.stderr)
        return 3
    dpi_text = argv.pop()
    prefix = argv.pop()
    folder = argv.pop()
    document = fitz.open(argv.pop())
    dpi = int(dpi_text)
    total = 0
    for number in range(document.page_count):
        name = "%s-p%02d.png" % (prefix, number + 1)
        destination = os.path.join(folder, name)
        page_image = document.load_page(number).get_pixmap(dpi=dpi)
        page_image.save(destination)
        total += 1
    document.close()
    print("OK rasterized %d page image(s) at %d dpi" % (total, dpi))
    return 0


sys.exit(rasterize(sys.argv[1:]))
'@

function Stop-WithIncomplete([int]$Code, [string]$LogLine, [string]$Message) {
    Write-Line $LogLine
    Write-Line ('RENDER-EXIT:' + $Code)
    Write-WorkerFailure $Message
    exit $Code
}

# `python` when it is on PATH, otherwise the Windows `py` launcher; $null when neither is.
function Get-Python {
    @('python', 'py') | Where-Object { Get-Command $_ -ErrorAction SilentlyContinue } | Select-Object -First 1
}

function New-PageImages([string]$PdfPath, [string]$Folder, [string]$Stem) {
    $helper = Join-Path $env:TEMP ('dlrv_' + [guid]::NewGuid().ToString('N') + '.py')
    $captured = @()
    $status = $null
    # Python may print a harmless warning on stderr. Windows PowerShell 5.1 raises the first
    # such line from a redirected native call as an error, and under Stop that error would
    # end the worker, so the preference drops to Continue for this one call.
    $keep = $ErrorActionPreference
    $ErrorActionPreference = 'Continue'
    try {
        [System.IO.File]::WriteAllText($helper, $script:RasterizerSource, (New-Object System.Text.UTF8Encoding($false)))
        $python = Get-Python
        if ($python) {
            $captured = @(& $python $helper $PdfPath $Folder $Stem $Dpi 2>&1 | ForEach-Object { [string]$_ })
            $status = $LASTEXITCODE
        } else {
            $captured = @('neither python nor py was found on PATH')
        }
    } catch {
        $captured += $_.Exception.Message
    } finally {
        $ErrorActionPreference = $keep
        Remove-Quietly $helper
    }

    $report = ($captured -join [Environment]::NewLine).Trim()
    if ($report) { Write-Line $report }

    if ($null -eq $status -or $status -ne 0) {
        if ($null -eq $status) { $reason = 'python never ran' } else { $reason = 'the rasterizer exited with ' + $status }
        Stop-WithIncomplete 5 ('page images: FAILED, ' + $reason) ('RENDER INCOMPLETE: the PDF ' + $PdfPath + ' was produced but its page images were not (' + $reason + '). The deliverable is UNREVIEWED.')
    }
}

function Confirm-PageImages([string]$PdfPath, [string]$Folder, [string]$Stem) {
    $answer = $null
    $keep = $ErrorActionPreference
    $ErrorActionPreference = 'Continue'
    try {
        $answer = & (Get-Python) -c "import sys, fitz; print(fitz.open(sys.argv[1]).page_count)" $PdfPath 2>$null
    } catch {
        $answer = $null
    } finally {
        $ErrorActionPreference = $keep
    }

    $total = 0
    $lastLine = [string](@($answer) | Where-Object { "$_".Trim() } | Select-Object -Last 1)
    $readable = [int]::TryParse($lastLine.Trim(), [ref]$total)
    $images = @(Get-ChildItem -LiteralPath $Folder -File | Where-Object { Test-IsPageImage $_.Name $Stem }).Count

    if (-not $readable -or $total -le 0) {
        Stop-WithIncomplete 6 ('page count: the PDF page total could not be read; {0} page image(s) on disk' -f $images) ('RENDER INCOMPLETE: the page total of ' + $PdfPath + ' was unreadable, so the ' + $images + ' page image(s) could not be checked. The deliverable is UNREVIEWED.')
    }
    if ($images -ne $total) {
        Stop-WithIncomplete 6 ('page count: MISMATCH, {0} page image(s) for {1} PDF page(s)' -f $images, $total) ('RENDER INCOMPLETE: ' + $images + ' page image(s) were written for a PDF of ' + $total + ' page(s). The deliverable is UNREVIEWED.')
    }
    Write-Line ('OK page images: {0} of {1} page(s)' -f $images, $total)
}

function Invoke-WorkerMode {
    $source = (Resolve-Path -LiteralPath $In).ProviderPath
    $folder = (Resolve-Path -LiteralPath $Out).ProviderPath
    $extension = [System.IO.Path]::GetExtension($source).ToLowerInvariant()
    $stem = Get-RenderStem $source
    $pdfPath = Join-Path $folder ($stem + '.pdf')
    $isDeck = $script:DeckTypes -contains $extension

    try {
        switch ($extension) {
            { $_ -eq '.pptx' -or $_ -eq '.ppt' } { Export-Deck $source (Join-Path $folder $stem); break }
            { $_ -eq '.docx' -or $_ -eq '.doc' } { Export-WordFile $source $extension $pdfPath; break }
            { $_ -eq '.xlsx' -or $_ -eq '.xls' } { Export-Workbook $source $pdfPath; break }
            default { throw ('Unsupported file type: ' + $extension + ' (supported: ' + ($script:KnownTypes -join ', ') + ')') }
        }
    } finally {
        try { Clear-OldScratch } catch { }
    }

    if (-not $NoPng -and -not $isDeck -and (Test-Path -LiteralPath $pdfPath)) {
        New-PageImages $pdfPath $folder $stem
        Confirm-PageImages $pdfPath $folder $stem
    }

    Write-Line 'RENDER-OK'
    exit 0
}

# ------------------------------------------------------------------ parent mode ---

# Parent output uses PowerShell's own streams: lines go to the success stream (stdout under
# -File) and failures to the error stream (stderr under -File), so an in-session caller can
# capture or redirect both. No parent helper returns a value, so nothing gets mixed in.
function Send-Line([string]$Text) {
    Write-Output $Text
}

# Writes a non-terminating error, so the documented exit code that follows still applies
# under the Stop preference. Callers keep each line short: the console host wraps error
# text at its width, and short lines keep every number and marker whole.
function Write-RenderError([string[]]$Lines) {
    Write-Error -Message ($Lines -join [Environment]::NewLine) -Category NotSpecified -ErrorId 'RenderDeliverable' -ErrorAction Continue
}

# Start-Process joins its argument list with spaces and adds no quoting of its own, so every
# path is wrapped here. A trailing backslash is doubled so it cannot escape the quote.
function Format-ChildArgument([string]$Value) {
    if ($Value.EndsWith('\')) { $Value = $Value + '\' }
    return '"' + $Value + '"'
}

# The worker may still hold these files open, so read them with full sharing.
function Read-SharedText([string]$Path) {
    if (-not [System.IO.File]::Exists($Path)) { return '' }
    try {
        $stream = New-Object System.IO.FileStream($Path, [System.IO.FileMode]::Open, [System.IO.FileAccess]::Read, ([System.IO.FileShare]::ReadWrite -bor [System.IO.FileShare]::Delete))
        try {
            $reader = New-Object System.IO.StreamReader($stream, [System.Text.Encoding]::UTF8, $true)
            return $reader.ReadToEnd().Trim()
        } finally {
            $stream.Dispose()
        }
    } catch {
        return ''
    }
}

function Get-DeliverableArtifacts([string]$Folder, [string]$Stem, [bool]$IsDeck) {
    if ($IsDeck) {
        $deckFolder = Join-Path $Folder $Stem
        if (-not (Test-Path -LiteralPath $deckFolder -PathType Container)) { return , @() }
        $found = @(Get-ChildItem -LiteralPath $deckFolder -Filter 'Slide*.PNG' -File | Where-Object { $_.Name -like 'Slide*.PNG' })
    } else {
        $found = @(Get-ChildItem -LiteralPath $Folder -File | Where-Object { $_.Name -eq ($Stem + '.pdf') -or (Test-IsPageImage $_.Name $Stem) })
    }
    return , @($found | Sort-Object Name)
}

function Invoke-ParentMode {
    if (-not (Test-Path -LiteralPath $In)) {
        throw ('Input not found: ' + $In + '. Nothing was rendered; the deliverable is UNREVIEWED.')
    }

    $source = (Resolve-Path -LiteralPath $In).ProviderPath
    $sourceFolder = [System.IO.Path]::GetDirectoryName($source)
    $baseName = [System.IO.Path]::GetFileNameWithoutExtension($source)
    $extension = [System.IO.Path]::GetExtension($source).ToLowerInvariant()
    $stem = Get-RenderStem $source

    if ($script:KnownTypes -notcontains $extension) {
        throw ('Unsupported file type: ' + $extension + ' (supported: ' + ($script:KnownTypes -join ', ') + '). Nothing was rendered; the deliverable is UNREVIEWED.')
    }
    $isDeck = $script:DeckTypes -contains $extension

    if (-not (Test-Path -LiteralPath $Out)) {
        [void](New-Item -ItemType Directory -Path $Out)
    }
    $folder = (Resolve-Path -LiteralPath $Out).ProviderPath

    if ($folder.TrimEnd('\') -ieq $sourceFolder.TrimEnd('\')) {
        throw ('-Out must not be the folder that holds the input (' + $sourceFolder + '). Pass a scratch folder instead. Nothing was rendered; the deliverable is UNREVIEWED.')
    }

    $worstCase = Get-WorstCasePath $folder $stem $isDeck
    if ($worstCase.Length -gt $script:UsablePathLimit) {
        $excess = $worstCase.Length - $script:UsablePathLimit
        Write-RenderError @(
            ('Refused before rendering: the path budget is exceeded by {0} character(s).' -f $excess),
            ('The longest artifact would need {0} characters; the ceiling is {1}' -f $worstCase.Length, $script:UsablePathLimit),
            '(MAX_PATH = 260, one of which is the terminating null). The path in question:',
            $worstCase,
            ('Move -Out somewhere at least {0} character(s) shorter and try again.' -f $excess),
            'A \\?\ prefix will not rescue it, since Word COM disregards that form.',
            'The deliverable remains UNREVIEWED.'
        )
        exit 7
    }

    if ($isDeck) {
        Send-Line ('artifacts: {0}\Slide*.PNG  <-  {1}{2}' -f $stem, $baseName, $extension)
    } else {
        Send-Line ('artifacts: {0}.pdf / {0}-pNN.png  <-  {1}{2}' -f $stem, $baseName, $extension)
    }

    # Remove only this deliverable's earlier artifacts, by exact name. Never recursive.
    foreach ($stale in (Get-DeliverableArtifacts $folder $stem $isDeck)) {
        try { Remove-Item -LiteralPath $stale.FullName -Force -ErrorAction Stop } catch { }
    }

    $runId = [guid]::NewGuid().ToString('N')
    $ownedPath = Join-Path $env:TEMP ('dlrv_owned_' + $runId + '.txt')
    $stdoutPath = Join-Path $env:TEMP ('dlrv_stdout_' + $runId + '.txt')
    $stderrPath = Join-Path $env:TEMP ('dlrv_stderr_' + $runId + '.txt')
    [System.IO.File]::WriteAllText($ownedPath, '', [System.Text.Encoding]::ASCII)

    $shell = $null
    try { $shell = (Get-Process -Id $PID).Path } catch { }
    if (-not $shell) { $shell = 'powershell.exe' }

    $childArgs = @(
        '-NoProfile', '-NonInteractive',
        '-File', (Format-ChildArgument $PSCommandPath),
        '-In', (Format-ChildArgument $source),
        '-Out', (Format-ChildArgument $folder),
        '-Dpi', [string]$Dpi,
        '-Worker',
        '-PidFile', (Format-ChildArgument $ownedPath)
    )
    if ($NoPng) { $childArgs += '-NoPng' }

    $timer = [System.Diagnostics.Stopwatch]::StartNew()
    $child = Start-Process -FilePath $shell -ArgumentList $childArgs -WindowStyle Hidden -PassThru `
        -RedirectStandardOutput $stdoutPath -RedirectStandardError $stderrPath
    # Touching the handle early keeps ExitCode readable on Windows PowerShell 5.1.
    $null = $child.Handle
    $done = $child.WaitForExit($TimeoutSec * 1000)

    if (-not $done) {
        $timer.Stop()
        Send-Line '--- worker output up to the stall ---'
        $partOut = Read-SharedText $stdoutPath
        $partErr = Read-SharedText $stderrPath
        if ($partOut) { Send-Line $partOut }
        if ($partErr) { Send-Line $partErr }

        try { $child.Kill() } catch { }
        Start-Sleep -Milliseconds 500

        $ownedLines = @()
        if ([System.IO.File]::Exists($ownedPath)) {
            $ownedLines = @([System.IO.File]::ReadAllLines($ownedPath) | ForEach-Object { $_.Trim() })
        }
        $recorded = @($ownedLines | Where-Object { $_ -match '^\d+$' } | Select-Object -Unique)
        $startOf = @{}
        foreach ($line in $ownedLines) {
            if ($line -match '^start:(\d+):(\d+)$') { $startOf[[int]$Matches[1]] = [long]$Matches[2] }
        }

        if ($recorded.Count -gt 0) {
            Send-Line 'timeout: ending only the Office instance(s) this render started'
            foreach ($entry in $recorded) {
                $id = [int]$entry
                $ticks = [long]0
                if ($startOf.ContainsKey($id)) { $ticks = $startOf[$id] }
                $state = Get-OwnedProcessState $id $ticks
                if ($state -eq 'alive') {
                    try {
                        Stop-Process -Id $id -Force -ErrorAction Stop
                        Send-Line ('timeout: ended PID ' + $id)
                    } catch {
                        Send-Line ('timeout: PID ' + $id + ' could not be ended: ' + $_.Exception.Message)
                    }
                } elseif ($state -eq 'unproven') {
                    Send-Line ('timeout: PID ' + $id + ' has no recorded start time, so it is left running')
                } elseif ($state -eq 'reused') {
                    Send-Line ('timeout: PID ' + $id + ' now names another process (reused, left alone)')
                } else {
                    Send-Line ('timeout: PID ' + $id + ' was already gone')
                }
            }
        } else {
            Send-Line 'timeout: the render had attached to an Office instance that was already open, so nothing is ended. Close that Office app and run again.'
        }

        Remove-Quietly $ownedPath
        Remove-Quietly $stdoutPath
        Remove-Quietly $stderrPath
        $seconds = $timer.Elapsed.TotalSeconds.ToString('0.0', [System.Globalization.CultureInfo]::InvariantCulture)
        Write-RenderError @(
            ('RENDER TIMEOUT after {0} s (limit -TimeoutSec {1}). Input:' -f $seconds, $TimeoutSec),
            $source,
            'Nothing was rendered and the deliverable stays UNREVIEWED.',
            'Office sessions that were already open were left running.',
            'Raise -TimeoutSec, or close the Office app and run again.'
        )
        exit 2
    }

    $child.WaitForExit()
    $timer.Stop()

    $workerOut = Read-SharedText $stdoutPath
    $workerErr = Read-SharedText $stderrPath
    if ($workerOut) { Send-Line $workerOut }
    if ($workerErr) {
        Send-Line '--- worker stderr ---'
        Send-Line $workerErr
    }

    $code = $child.ExitCode
    if ($null -eq $code) {
        $fallback = [regex]::Match($workerOut, 'RENDER-EXIT:(\d+)')
        if ($fallback.Success) { $code = [int]$fallback.Groups[1].Value }
    }
    $reachedEnd = $workerOut.Contains('RENDER-OK')
    $codeKnown = $null -ne $code
    if ($codeKnown) { $codeText = [string]$code } else { $codeText = 'unknown' }

    Remove-Quietly $ownedPath
    Remove-Quietly $stdoutPath
    Remove-Quietly $stderrPath

    $produced = Get-DeliverableArtifacts $folder $stem $isDeck
    $seconds = $timer.Elapsed.TotalSeconds.ToString('0.0', [System.Globalization.CultureInfo]::InvariantCulture)
    Send-Line ('=== artifacts after ' + $seconds + ' s ===')
    if ($produced.Count -gt 0) {
        Send-Line (($produced | Format-Table Name, Length -AutoSize | Out-String -Width 4096).Trim())
    } else {
        Send-Line 'no render artifacts were produced'
    }

    if ($produced.Count -eq 0) {
        Write-RenderError @(
            ('RENDER PRODUCED NOTHING (worker exit {0}). Input:' -f $codeText),
            $source,
            'The deliverable is UNREVIEWED.'
        )
        exit 3
    }
    if ($codeKnown -and (@(5, 6) -contains $code)) {
        Write-RenderError @(
            ('RENDER INCOMPLETE (worker exit {0}): the PDF exists, but its page images' -f $code),
            'are missing or incomplete. The deliverable is UNREVIEWED.'
        )
        exit $code
    }
    if (-not $reachedEnd) {
        Write-RenderError @(
            ('RENDER INCOMPLETE (worker exit {0}): the worker never printed its' -f $codeText),
            'success marker RENDER-OK. The deliverable is UNREVIEWED.'
        )
        exit 4
    }
    if ($codeKnown -and $code -ne 0) {
        Write-RenderError @(
            ('RENDER FAILED: the worker exited with code {0}.' -f $code),
            'The deliverable is UNREVIEWED.'
        )
        exit $code
    }
    exit 0
}

if ($Worker) {
    Invoke-WorkerMode
} else {
    Invoke-ParentMode
}
