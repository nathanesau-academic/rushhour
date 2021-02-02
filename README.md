# Rush Hour - An A* Implementation

simplified version of code re-written in python.

## References

Level Editor:

* https://nathanesau.github.io/rushhour_wasm/rushhour.html

## Background

Input Grid Format:

```
bb...g
a..c.g
axxc.g
a..c..
a..c..
e.ddd.
```

Parsed Grid Format (replace characters with numbers):

```
+2 +2 -1 -1 -1 +7
+1 -1 -1 +3 -1 +7
+1 +0 +0 +3 -1 +7
+1 -1 -1 +3 -1 -1
+5 -1 -1 -1 +6 +6
+5 -1 +4 +4 +4 -1
```

Transposed, Parsed Grid Format (transpose parsed grid):

<!-- NOTE: this is the format used in the original java code 
  TO BE REMOVED

```
+2 +1 +1 +1 +5 +5
+2 -1 +0 -1 -1 -1
-1 -1 +0 -1 -1 +4 
-1 +3 +3 +3 -1 +4
-1 -1 -1 -1 +6 +4
+7 +7 +7 -1 +6 -1
```

-->