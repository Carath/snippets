#!/bin/sh

# Note: this script relies on the /bin/time and bc commands.

help="This script runs several instances of a target to benchmark,
and outputs statistics on recorded RAM usage and runtimes.
The target may be an executable file, or a symbolic link
to one (like most bash commands). Arguments:

  t=  The target to run. It may have args, if so said target
      and args must be enclosed in quotes, see the example below.
      Also, the target can be given as first argument without using t=...

  n=  The number of runs (optional, default: 10).

  v=  The verbosity level (optional, default: 0).
      When >= 1, the target outputs are printed.
      When >= 2, the list of runtimes is also printed.

  s=  The strictness level (optional, default: 1).
      With 1, exit codes will be checked and failed runs will be ignored.

  r=  A reference value to be compared with the average runtime (optional).

Usage example: sh benchmark.sh \"target somearg\" n=2 v=1 s=1 r=1.5
To open the help: sh benchmark.sh -help"

LC_ALL=C # Setting '.' as decimal separator, bypassing the system locale.

target=$1
case "$1" in
	"" | -help | --help)
		printf "$help\n"; exit 0 ;;
	*=*)
		target="" ;;
esac

for arg in "$@"; do
	key=$(echo $arg | cut -f1 -d=)
	value=$(echo $arg | cut -f2 -d=)
	case "$key" in
		t)      target=${value} ;;
		n)        runs=${value} ;;
		v)   verbosity=${value} ;;
		s)  strictMode=${value} ;;
		r)         ref=${value} ;;
		*)
	esac
done

isInteger() {
	if [ "$1" -eq "$1" ] 2> /dev/null; then
		return "1"
	fi
	return "0"
}

if [ -z "$target" ]; then
	echo "Please provide a target to benchmark."; exit 1
fi

targetPath=$(which $(echo $target | awk '{print $1}'))
if [ -z "$targetPath" ]; then
	echo "Invalid target: $target"; exit 1
fi

if [ -z $runs ]; then
	runs=10 # default
fi
isInteger $runs
if [ $? -eq 0 ] || [ $runs -le 0 ]; then
	echo "Number of runs ($runs) must be an integer > 0"; exit 1
fi

if [ -z $verbosity ]; then
	verbosity=0 # default
fi
isInteger $verbosity
if [ $? -eq 0 ]; then
	echo "Verbosity level ($verbosity) must be an integer."; exit 1
fi

if [ -z $strictMode ]; then
	strictMode=1 # default
fi
isInteger $strictMode
if [ $? -eq 0 ]; then
	echo "Strictness level ($strictMode) must be an integer."; exit 1
fi

if [ ! -z $ref ] && [ $(echo "$ref <= 0" | bc -l) -eq 1 ]; then
	echo "Reference value ($ref) must be > 0"; exit 1
fi

timeCommand=$(which time)
echo "Found time command: $timeCommand"
smallhash=$(md5sum $targetPath | cut -c 1-10)
printf "Launching %d run(s) of: %s\nTarget md5sum: %s...\n\n" $runs "$target" $smallhash
maxRAM=0; totalTime=0; sumSquares=0; successes=0; times=""
for i in $(seq 1 $runs); do
	# Note: using target instead of targetPath here, in order to use its args.
	start=$(date +%s.%N)
	output=`($timeCommand -f "RAM: %M" $target) 2>&1`; exitCode=$?
	end=$(date +%s.%N)
	runtime=$(echo "$end - $start" | bc -l)
	RAM=$(echo "$output" | awk '/RAM/{print $NF}')
	if [ $strictMode -eq 0 ] || [ $exitCode -eq 0 ]; then
		totalTime=$(echo "$totalTime + $runtime" | bc -l)
		sumSquares=$(echo "$sumSquares + $runtime^2" | bc -l)
		times="$times $runtime"
		successes=$((successes+1))
		if [ $RAM -gt $maxRAM ]; then
			maxRAM=$RAM
		fi
	fi
	if [ $verbosity -ge 1 ] || [ $exitCode -ne 0 ]; then
		echo "$output\n"
	fi
	printf "Run %d:\n Exit code: %d\n RAM peak:  %d KB\n Runtime:   %.3f s\n\n" $i $exitCode $RAM $runtime
	if [ $verbosity -ge 1 ]; then
		printf "%25s\n\n" | tr " " "-"
	fi
done
maxRAM=$(echo "$maxRAM / 1000" | bc -l)

medianTime=$(printf "%f\n" $times | sort -g | awk '{ a[i++]=$1; } END { print (a[int((i-1)/2)] + a[int(i/2)])/2; }')
avgTime=0
if [ $successes -gt 0 ]; then
	avgTime=$(echo "$totalTime / $successes" | bc -l)
fi

# With Bessel's correction:
stdDev=0
if [ $successes -gt 1 ]; then
	stdDev=$(echo "sqrt(($sumSquares - $successes * $avgTime^2) / ($successes-1))" | bc -l)
fi

if [ $verbosity -ge 2 ]; then
	printf "Times: $times\n\n"
fi

failures=$((runs - successes))
if [ $failures -ne 0 ]; then
	printf "=> %d run(s) finished with a non-zero exit code.\n" $failures
fi

printf "=> Max RAM peak:  %.0f MB\n" $maxRAM
printf "=> Time median:   %.3f s\n" $medianTime
printf "=> Time average:  %.3f s\n" $avgTime
printf "=> Time std-dev:  %.3f s\n" $stdDev

if [ ! -z $ref ]; then
	relatDiff=$(echo "($avgTime / $ref - 1) * 100" | bc -l)
	printf "=> (avg-ref)/ref: %.3f %%\n" $relatDiff
fi
