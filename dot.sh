#!/bin/bash
for f in `ls ./output/*.dot`; do
    echo "Rendering $f into PNG..."
    dot -Tpng $f -O
done

