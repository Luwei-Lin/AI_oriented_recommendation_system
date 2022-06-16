
# Notes

## Some confusions of the JSON

1. (√)tops has two "shirt" tag.

2. (√)Don't need 's' for each type. No worries, We can deal with this by lemma_.

3. '/' Can directly seperate two parts.

4. (√)other_clothing:' jumpsuits and rompers ' -> 'jumpsuit', 'romper'

5. (√)accessories: 'Ties and Pocket Squares' -> 'tie', 'pocket square'

6. (√)'heel' in 'shoe_type' and 'heel cover' in 'accessories', nlp might detect these two item to heel and heel cover both... so do We need to modify heel shoes or something else?

7. (√)'socks and tights' (Accessories) -> matcher filters: 'sock', 'tight' instead of 'sock and tight'

8. (√)'area rug' (homeware) can be replaced by just 'rug'?

9. (√)'bath mat' (homeware) can be replaced by just 'mat'?

10. (X)add 'shrunken', 'sleeve' in the top styles

## Update May 19

1. (√)add 'tee' and 't' in 'tops'
2. (√)'tanktop' in tops instead of 'tank top'
3. (√)'croptop' and 'croptee' are new items found and could be added in 'tops' or 'shirt'

## Update May 21

1. (√)can add 'Puzzle' in other
2. (√)can add 'Clip' in accessories (hair clips)
3. (√)can add 'Scrunchies' in accessories(hair scrunchie)
4. (√)There are some food types (for now we add to 'other')
5. (√)new Item 'Cloak' is found , which could be added to 'other_clothing'

## Update June 14

1. (√)'swimsuit' in other_clothing, swimwear
2. (√)'hat' in acc, headwear
3. (√)'pant' in bottom
4. (√)'pyrrha' in acc
5. (√)'perfume' in beauty

## Update June 15

1. (√)'knitwear' to 'tops'
2. (√)'culotte' to 'bottoms' might be after 'pants' because 'culotte jeans' already in jeans.
3. 'strap' could be ambiguous, could be 'accessories' or 'tops', 'bottoms'
4. 'clothing' product type is ambiguous, we might need to check title as well before we did matches.

5. 'unclassified' but the title has the specific type like 'men's top'.

6. product_type has '-' punctuation, like 'tops - casual', 'bottoms - trousers', 'bottoms - skirts', 'accessories - scarves', 'coats + jackets' etc. The similarity method cannot match to predefined string (> 60 % similarity)

7. (√)'intimate' could be added to 'tops'.
8. (√)'textile' could be added to 'homeware'.
9. (√)'Clog' added to 'shoes'.

10. (√)'ceramics' --> 'homeware'

11. (√)'sweetleg' to 'bottom'

12. 'remove women and men, ladies, boys, girl(Noun) and 'premium', 'graphic'(adj) in the product-type when matches before we implement match algorithm with new all_cat.
13. no 'romper' ?

14. (√)add 'croptop' in 'tops'

15. 'sleeve' could be ambiguous, "long sleeve short(TOPS)" and "sleeves(Accessories)". add short sleeve shirt, "long sleeve shirt", "sleeveless" to tops

16. (√)add "swim trunk" to "swimwear"

17. (√)separate "blanket/towel" to "blanket" and "towel"

18. (√)Add "Bandana" to "Accessories"

19. (√)Add "Drop Tee"to "Shirts"

20. (√)Add "Sleeveless hoodie", "Zip up hoodie" and "Crop hoodie" to "Sweater"

21. (√) Add "Face Masks" to "skin care"

22. (√) Add "Raverback tank", to "tops"

23. (√) Remove the "jump & romper" from "dresses", they belong to other_clothing.

24. if the 80% matches is missed, but the 60 % exist, we can use the similarity to compare both, and then if the similarity is higher than 0.6, we regard it as the product-type we pre-defined. 

25. (√) add "bodycon dress" in "dress"

26. (√) add "booty shorts" in ""