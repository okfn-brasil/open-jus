#!/usr/bin/env python
import argparse

import rows

from budget_base import get_actions_for_state, Action
from budget_sp import SaoPauloBudgetExecutionSpider


spiders = {"SP": SaoPauloBudgetExecutionSpider}


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("state", choices=spiders.keys())
    parser.add_argument("--year", type=int)
    parser.add_argument("--action", type=int)
    parser.add_argument("--quiet", action="store_true")
    parser.add_argument("--headless", action="store_true")
    args = parser.parse_args()
    if args.year is None and args.action is None:
        actions = get_actions_for_state(args.state)
    elif args.action is None:
        actions = [
            action
            for action in get_actions_for_state(args.state)
            if action.year == args.year
        ]
    else:
        actions = [
            Action(year=args.year, code=args.action, state=args.state, name="Unknown")
        ]

    spider = spiders[args.state](headless=args.headless)
    for action in actions:
        if not args.quiet:
            print(
                f"Downloading budget execution for {action.state} ({action.code} @ {action.year})"
            )
        table = spider.execute(action.year, action.code)

        output_filename = f"{action.state}-{action.year}-{action.code}.csv"
        rows.export_to_csv(table, output_filename)
        if not args.quiet:
            print(f"  done (saved to {output_filename})")
    spider.close()


if __name__ == "__main__":
    main()
