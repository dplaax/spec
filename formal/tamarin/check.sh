#!/usr/bin/env bash
# Runs tamarin-prover on every lemma of a model, each in a process of its own
# (one after another, so that no run holds the memory of the others), and
# compares each result with the model's expectations. tamarin-prover exits 0
# also when a lemma is falsified, the analysis is incomplete or the model is
# not well-formed, so its summary is read, not its exit code.
#
# Usage: check.sh [MODEL [FLAG]]
#   MODEL     the model's file name without .spthy (chain, ...); without it,
#             every model in this directory is checked in its default build.
#   FLAG      a preprocessor flag passed as -D=FLAG (a negative control, such
#             as SkipLinkCheck); without it the default build is checked. A
#             FLAG that MODEL.expected.tsv does not name as a build is refused.
#   TIMEOUT   seconds per lemma (600 by default); a lemma that runs out of
#             time is unresolved, not falsified. GNU timeout is used when on
#             PATH; otherwise the run is killed from the shell.
#
# A lemma's result is one of verified, falsified, unresolved. MODEL.expected.tsv
# lists the expected result per build and lemma ("build<TAB>lemma<TAB>result",
# build is "default" or the FLAG); a lemma absent from the file is expected to
# be verified. The script exits 0 only when every lemma's result is the one
# expected. Needs tamarin-prover and maude on PATH.
set -uo pipefail
cd "$(dirname "$0")" || exit 1
timeout_s="${TIMEOUT:-600}"

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

# expected FILE BUILD LEMMA prints the expected result, verified when unlisted.
expected() {
	local want
	want=$(awk -F'\t' -v b="$2" -v l="$3" '$1 == b && $2 == l { print $3 }' "$1" 2>/dev/null | head -1)
	echo "${want:-verified}"
}

# check_model MODEL FLAG checks every lemma of MODEL.spthy in one build and
# returns 1 when any result is not the expected one.
check_model() {
	local name="$1" flag="$2"
	local model="$name.spthy" expected_file="$name.expected.tsv"
	local build="${flag:-default}"
	if [ ! -f "$model" ]; then
		echo "check.sh: no model $model"
		return 1
	fi
	# tamarin-prover ignores a -D flag the model does not use and checks the
	# default model, so a misspelled FLAG would pass as a build in which every
	# lemma holds. A FLAG is a build only when the expectations name it.
	if [ -n "$flag" ] && ! awk -F'\t' -v b="$flag" '$1 == b { found = 1 } END { exit !found }' "$expected_file" 2>/dev/null; then
		echo "check.sh: $flag is not a build in $expected_file"
		return 1
	fi
	local lemmas
	lemmas=$(sed -nE 's/^lemma ([A-Za-z0-9_]+).*/\1/p' "$model")
	if [ -z "$lemmas" ]; then
		echo "check.sh: no lemma in $model"
		return 1
	fi
	local args=()
	[ -n "$flag" ] && args+=("-D=$flag")
	local mismatch="" n_verified=0 n_falsified=0 n_unresolved=0
	local lemma start out status summary result want
	for lemma in $lemmas; do
		start=$(date +%s)
		# ${args[@]+...}: an empty array is "unbound" to bash 3.2 under set -u.
		out=$(bounded "$timeout_s" tamarin-prover ${args[@]+"${args[@]}"} --prove="$lemma" --derivcheck-timeout=600 "$model" 2>&1)
		status=$?
		# The summary lists every lemma; only this one's line is the result
		# (the others read "analysis incomplete", not proven in this run).
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
		want=$(expected "$expected_file" "$build" "$lemma")
		echo "${summary:-$lemma: no result} -> $result, expected $want ($(($(date +%s) - start)) s)"
		if [ "$result" != "$want" ]; then
			echo "$out"
			echo "check.sh: $lemma: $result, expected $want (tamarin-prover exited with $status)"
			mismatch="$mismatch $lemma"
		fi
	done
	echo "check.sh [$name/$build]: verified $n_verified, falsified $n_falsified, unresolved $n_unresolved"
	if [ -n "$mismatch" ]; then
		echo "check.sh [$name/$build]: mismatch:$mismatch"
		return 1
	fi
	echo "check.sh [$name/$build]: every lemma has its expected result"
}

if [ "$#" -gt 0 ]; then
	check_model "$1" "${2:-}"
	exit $?
fi
failed=""
found=""
for model in *.spthy; do
	[ -f "$model" ] || continue
	found=1
	check_model "${model%.spthy}" "" || failed="$failed ${model%.spthy}"
done
if [ -z "$found" ]; then
	echo "check.sh: no model in $(pwd)"
	exit 1
fi
if [ -n "$failed" ]; then
	echo "check.sh: models with a mismatch:$failed"
	exit 1
fi
