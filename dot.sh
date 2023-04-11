#!/bin/bash
for f in `ls ./output/*.dot`; do
    dot -Tpng $f -O
done

