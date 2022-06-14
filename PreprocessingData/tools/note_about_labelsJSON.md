
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

1. add 'tee' and 't' in 'tops'
2. 'tanktop' in tops instead of 'tank top'
3. 'crop', 'croptop' and 'croptee' are new items found and could be added in 'tops' or 'shirt'

## Update May 21

1. can add 'Puzzle' in other
2. can add 'Clip' in accessories (hair clips)
3. can add 'Scrunchies' in accessories(hair scrunchie)
4. There are some food types (for now we add to 'other')
5. new Item 'Cloak' is found , which could be added to 'other_clothing'? 

## Update June 14

1. 'swimsuit' in other_clothing, swimwear
2. 'hat' in acc, headwear
3. 'pant' in bottom
4. 'pyrrha' in acc
5. 'perfume' in beauty
