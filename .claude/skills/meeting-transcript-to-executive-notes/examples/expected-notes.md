# Overview

The Jira migration holds its April 2 cutover with no parallel run, which removes a second license bill. The PostgreSQL upgrade is about 70% complete, and the three reporting databases stay on their current version until the vendor certifies a driver. The monitoring vendor renewal is on hold until the price is negotiated, and the vendor's April 5 order date is at risk. A comparison of the retention schedule against the vendor's terms is under way, because the vendor's default deletes logs a year earlier than ours. Seven actions are recorded; one has no owner yet.

# By subject

## Jira migration

**Summary:** Cutover stays on April 2. The group dropped the sixty-day parallel run and settled on a freeze of new intake on the old system instead.

**Discussion:**
- Topic: Queue mappings are built and the new intake form has been tested twice; the April 2 date holds unless intake testing slips.
- Agreement: No parallel run. New intake on the old system freezes the week before cutover, and the old queues go read-only at cutover. About forty tickets are in flight on a typical day, and they close out during the freeze.
- Issue: Running both systems for sixty days would have meant paying for two licenses, which did not justify forty tickets.
- Dependency: The old system's ticket export must be archived before the queues go read-only. Priya Shah owns the archive; Jordan Lee switches the queues over once it is done.
- Topic: The intake form lists the new queue names in a dropdown.

**Decisions:**
- No parallel run: the old queues go read-only at the April 2 cutover, and new intake on the old system freezes the week before.

**Actions:**
- Send agents the intake freeze notice | Owner: Jordan Lee | Due: March 26, 2030
- Archive the old system's ticket export before it goes read-only | Owner: Priya Shah | Due: April 1, 2030
- Update the intake form wording for the new queue names | Owner: Jordan Lee | Due: TBD

## PostgreSQL upgrade

**Summary:** About 70% of the databases are on the new version. The remaining three reporting databases wait on a vendor driver that is not yet certified.

**Discussion:**
- Topic: The migrated databases are stable, with no incidents since the first batch moved.
- Dependency: The three reporting databases rely on a vendor driver that is not certified for the new version. The vendor expects certification next quarter and has not given a firm date.
- Agreement: The reporting databases stay on the current version until the driver is certified. Priya Shah owns the follow-up with the vendor.

**Decisions:**
- The three reporting databases stay on the current version until the vendor certifies the driver.

**Actions:**
- Ask the vendor for a firm driver certification date | Owner: Priya Shah | Due: March 19, 2030

**Risks and blockers:**
- The reporting databases may stay on the older version for an unknown period, because the driver has no certification date.

## Monitoring vendor renewal

**Summary:** The vendor raised its quote and expects a signed order by April 5. Nothing is signed until the price is settled.

**Discussion:**
- Agreement: The order is not signed until the price is settled. Alex Rivera handles the price conversation.
- Topic: The vendor is to be told in writing that the renewal is under negotiation, so silence is not read as acceptance. No one owns the notice yet.
- Issue: The vendor's data deletion terms differ from ours, so the full contract needs a read before signing.
- Risk: Long price talks could pass the vendor's April 5 order date. An extension has not been requested; the first conversation comes first.

**Decisions:**
- No order is signed until the renewal price is settled.

**Actions:**
- Negotiate the renewal price with the vendor | Owner: Alex Rivera | Due: TBD
- Send the vendor written notice that the renewal is under negotiation | Owner: TBD | Due: March 29, 2030

**Open questions:**
- Whether the vendor's AI summarizer add-on for alert noise is covered by our data terms.

**Risks and blockers:**
- Price negotiation could run past the vendor's April 5 signed-order date.

## Retention schedule

**Summary:** The vendor's default log deletion is twelve months, against twenty-four in our schedule. A comparison of the two is in progress.

**Discussion:**
- Issue: The vendor deletes stored logs at twelve months, and our schedule requires twenty-four.
- Topic: The comparison of our schedule against the vendor's terms also covers whether the vendor can change its default.

**Actions:**
- Compare the retention schedule against the new vendor terms | Owner: likely Sam Okafor | Due: March 22, 2030

**Open questions:**
- Whether the vendor can change its default log deletion period.

**Risks and blockers:**
- Logs we are required to keep for another year would be lost if the vendor deletes at twelve months.

# All actions

- Send agents the intake freeze notice | Owner: Jordan Lee | Due: March 26, 2030 | Subject: Jira migration
- Archive the old system's ticket export before it goes read-only | Owner: Priya Shah | Due: April 1, 2030 | Subject: Jira migration
- Update the intake form wording for the new queue names | Owner: Jordan Lee | Due: TBD | Subject: Jira migration
- Ask the vendor for a firm driver certification date | Owner: Priya Shah | Due: March 19, 2030 | Subject: PostgreSQL upgrade
- Negotiate the renewal price with the vendor | Owner: Alex Rivera | Due: TBD | Subject: Monitoring vendor renewal
- Send the vendor written notice that the renewal is under negotiation | Owner: TBD | Due: March 29, 2030 | Subject: Monitoring vendor renewal
- Compare the retention schedule against the new vendor terms | Owner: likely Sam Okafor | Due: March 22, 2030 | Subject: Retention schedule

# All decisions

- No parallel run: the old queues go read-only at the April 2 cutover, and new intake on the old system freezes the week before. | Subject: Jira migration
- The three reporting databases stay on the current version until the vendor certifies the driver. | Subject: PostgreSQL upgrade
- No order is signed until the renewal price is settled. | Subject: Monitoring vendor renewal

# All open questions

- Whether the vendor's AI summarizer add-on for alert noise is covered by our data terms. | Subject: Monitoring vendor renewal
- Whether the vendor can change its default log deletion period. | Subject: Retention schedule

# All risks and blockers

- The reporting databases may stay on the older version for an unknown period, because the driver has no certification date. | Subject: PostgreSQL upgrade
- Price negotiation could run past the vendor's April 5 signed-order date. | Subject: Monitoring vendor renewal
- Logs we are required to keep for another year would be lost if the vendor deletes at twelve months. | Subject: Retention schedule
