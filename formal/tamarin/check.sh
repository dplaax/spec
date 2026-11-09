#!/usr/bin/env bash
# Runs tamarin-prover on every lemma of chain.spthy, each in a process of its
# own (one after another, so that no run holds the memory of the others), and
# compares each result with the expectation in expected.tsv. tamarin-prover
# exits 0 also when a lemma is falsified, the analysis is incomplete or the
# model is not well-formed, so its summary is read, not its exit code.
#
# Usage: check.sh [FLAG]
#   FLAG      a preprocessor flag passed as -D=FLAG (a negative control, such
#             as SkipLinkCheck); without it the default model is checked.
#   TIMEOUT   seconds per lemma (600 by default); a lemma that runs out of
#             time is unresolved, not falsified. GNU timeout is used when on
#             PATH; otherwise the run is killed from the shell.
#
# A lemma's result is one of verified, falsified, unresolved. expected.tsv
# lists the expected result per build and lemma ("build<TAB>lemma<TAB>result",
# build is "default" or the FLAG); a lemma absent from the file is expected to
# be verified. The script exits 0 only when every lemma's result is the one
# expected. Needs tamarin-prover and maude on PATH.
set -uo pipefail
cd "$(dirname "$0")"
model=chain.spthy
expected_file=expected.tsv
flag="${1:-}"
build="${flag:-default}"
timeout_s="${TIMEOUT:-600}"

if [ ! -f "$model" ]; then
	echo "check.sh: no model $model"
	exit 1
fi
lemmas=$(sed -nE 's/^lemma ([A-Za-z0-9_]+).*/\1/p' "$model")
if [ -z "$lemmas" ]; then
	echo "check.sh: no lemma in $model"
	exit 1
fi

# bounded SECONDS CMD... runs CMD, killing it after SECONDS: GNU timeout when
# there is one (exit 124), otherwise a background run and a kill (exit 143).
bounded() {
	local secs="$1"
	shift
	if command -v timeout >/dev/null 2>&1; then
		timeout "$secs" "$@"
	elif command -v gtimeout >/dev/null 2>&1; then
		gtimeout "$secs" "$@"
	else
		"$@" &
		local pid=$!
		# The killer holds no copy of stdout: a caller capturing the output
		# would otherwise wait for it to finish, not for the command.
		(sleep "$secs" && kill -TERM "$pid" 2>/dev/null) >/dev/null 2>&1 </dev/null &
		local killer=$!
		wait "$pid"
		local status=$?
		kill "$killer" 2>/dev/null
		wait "$killer" 2>/dev/null
		return "$status"
	fi
}

# expected BUILD LEMMA prints the expected result, verified when unlisted.
expected() {
	local want
	want=$(awk -F'\t' -v b="$1" -v l="$2" '$1 == b && $2 == l { print $3 }' "$expected_file" 2>/dev/null | head -1)
	echo "${want:-verified}"
}

args=()
[ -n "$flag" ] && args+=("-D=$flag")
mismatch=""
n_verified=0
n_falsified=0
n_unresolved=0
for lemma in $lemmas; do
	start=$(date +%s)
	# ${args[@]+...}: an empty array is "unbound" to bash 3.2 under set -u.
	out=$(bounded "$timeout_s" tamarin-prover ${args[@]+"${args[@]}"} --prove="$lemma" --derivcheck-timeout=600 "$model" 2>&1)
	status=$?
	# The summary lists every lemma; only this one's line is the result (the
	# others read "analysis incomplete", not proven in this run).
	summary=$(grep -E "^[[:space:]]*$lemma \((all-traces|exists-trace)\):" <<<"$out" | head -1 | sed -E 's/^[[:space:]]+//')
	if [ "$status" -eq 124 ] || [ "$status" -eq 143 ]; then
		result=unresolved
		summary="$lemma: timed out after ${timeout_s} s"
	elif grep -iq 'wellformedness check failed' <<<"$out"; then
		result=unresolved
		summary="$lemma: wellformedness check failed"
	elif grep -Eq "^[[:space:]]*$lemma \((all-traces|exists-trace)\): verified" <<<"$out"; then
		result=verified
	elif grep -Eq "^[[:space:]]*$lemma \((all-traces|exists-trace)\): falsified" <<<"$out"; then
		result=falsified
	else
		result=unresolved
	fi
	case "$result" in
		verified) n_verified=$((n_verified + 1));;
		falsified) n_falsified=$((n_falsified + 1));;
		unresolved) n_unresolved=$((n_unresolved + 1));;
	esac
	want=$(expected "$build" "$lemma")
	echo "${summary:-$lemma: no result} -> $result, expected $want ($(($(date +%s) - start)) s)"
	if [ "$result" != "$want" ]; then
		echo "$out"
		echo "check.sh: $lemma: $result, expected $want (tamarin-prover exited with $status)"
		mismatch="$mismatch $lemma"
	fi
done
echo "check.sh [$build]: verified $n_verified, falsified $n_falsified, unresolved $n_unresolved"
if [ -n "$mismatch" ]; then
	echo "check.sh: mismatch:$mismatch"
	exit 1
fi
echo "check.sh [$build]: every lemma has its expected result"
