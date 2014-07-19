#!/bin/sh

awk 'BEGIN { FS = "," } ; $5 ~ /^[0-9.-]+$/ && $6 ~ /^[0-9.-]+$/ {print $5,$6,$1,$2}' $1 \
		| awk '{a = $1 " " $2; if (!x[a]) {x[a]=a; print}}' \
		> $1.stripped

cat rough-outlines-corrected.txt >> $1.stripped
