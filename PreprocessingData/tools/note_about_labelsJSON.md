
# Notes

## Some confusions of the JSON

1. tops has two "shirt" tag.

2. Don't need 's' for each type.

3. '/' Can directly seperate two parts.

4. other_clothing:' jumpsuits and rompers ' -> 'jumpsuit', 'romper'

5. accessories: 'Ties and Pocket Squares' -> 'tie', 'pocket square'

6. 'heel' in 'shoe_type' and 'heel cover' in 'accessories', nlp might detect these two item to heel and heel cover both... so do We need to modify heel shoes or something else?

7. 'socks and tights' (Accessories) -> matcher filters: 'sock', 'tight' instead of 'sock and tight'

8. 'area rug' (homeware) can be replaced by just 'rug'?

9. 'bath mat' (homeware) can be replaced by just 'mat'?

10. add 'shrunken', 'sleeve' in the top styles

## Update May 19

1. add 'tee' in 'tops'
2. 'tanktop' in tops instead of 'tank top'
3. 'croptop' and 'croptee' is new item found and could be added in 'tops'
