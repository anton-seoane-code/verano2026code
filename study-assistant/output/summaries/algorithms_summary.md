# Summary: algorithms.txt

Binary search is an efficient algorithm for finding an item from a sorted list of items.

It works by repeatedly dividing in half the portion of the list that could contain the item, until you have narrowed down the possible locations to just one.

Binary search runs in logarithmic time O(log n), making it much faster than linear search for large datasets.

To implement binary search, you start with two pointers: left at index 0 and right at the last index.

You calculate the middle index and compare the value at that position with your target.
