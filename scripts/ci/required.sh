#!/usr/bin/env bash
# Expose one stable required check while retaining all reusable validations.
set -euo pipefail
for check in QUALITY_RESULT TESTS_RESULT SECURITY_RESULT PINNING_RESULT; do
	result="${!check}"
	if [[ "$result" != success ]]; then
		echo "A required validation did not succeed: $check=$result" >&2
		exit 1
	fi
done
if [[ "$GITHUB_EVENT_NAME" == pull_request || "$GITHUB_EVENT_NAME" == merge_group ]]; then
	for check in QUALITY_SUMMARY_RESULT SECURITY_SUMMARY_RESULT; do
		result="${!check}"
		if [[ "$result" != success && "$result" != skipped ]]; then
			echo "A required report failed: $check=$result" >&2
			exit 1
		fi
	done
	if [[ "$TITLE_RESULT" != success ]]; then
		echo "PR title validation did not succeed: $TITLE_RESULT" >&2
		exit 1
	fi
fi
