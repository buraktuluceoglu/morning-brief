import sys

import agents.cluster as cluster
import agents.collector as collector
import agents.dedupe as dedupe
import agents.filter as news_filter
import agents.mailer as mailer
import agents.summarizer as summarizer
from agents.dedupe import write_vault


def main() -> None:
    print("Collecting feeds...")
    raw = collector.collect()
    print(f"  {len(raw['items'])} fetched")

    print("Filtering by interests...")
    filtered = news_filter.filter_items(raw)
    print(f"  {len(filtered['items'])} after filter")

    print("Deduplicating against vault...")
    deduped = dedupe.dedupe(filtered)
    print(f"  {len(deduped['items'])} after dedupe")

    print("Clustering similar topics...")
    clustered = cluster.cluster(deduped)
    print(f"  {len(clustered['items'])} after cluster")

    if not clustered["items"]:
        print("Nothing new today.")
        sys.exit(0)

    print("Summarizing with Claude...")
    summarized = summarizer.summarize(clustered)

    print("Sending mail...")
    if mailer.send_mail(summarized):
        write_vault(clustered)
    else:
        print("Mail failed — vault not updated, will retry tomorrow")
        sys.exit(1)


if __name__ == "__main__":
    main()
