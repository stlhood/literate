# Example Text Samples for Testing Literate

This file contains various text samples for testing the narrative object extraction capabilities of Literate. Copy and paste these into the application to see how it identifies people, places, events, and relationships.

## Simple Examples

### Example 1: Basic Meeting
```
Alice met Bob at the coffee shop. They discussed their upcoming trip to Paris.
```
**Expected Objects:** Alice, Bob, coffee shop, Paris
**Expected Relationships:** Alice-Bob (met at coffee shop), Alice-Paris (upcoming trip), Bob-Paris (upcoming trip)

### Example 2: Family Dinner
```
Sarah invited her brother Tom to dinner at their mother's house. They enjoyed Mom's famous lasagna together.
```
**Expected Objects:** Sarah, Tom, mother/Mom, house, lasagna
**Expected Relationships:** Sarah-Tom (siblings), Sarah-Mom (mother-daughter), Tom-Mom (mother-son)

## Intermediate Examples

### Example 3: Business Meeting
```
The CEO Rachel announced the quarterly results to the board of directors in the conference room. 
CFO Michael presented the financial projections, while Marketing Director Lisa outlined the new campaign strategy.
```
**Expected Objects:** Rachel (CEO), Michael (CFO), Lisa (Marketing Director), board of directors, conference room, quarterly results, financial projections, campaign strategy
**Expected Relationships:** Various professional relationships and meeting context

### Example 4: Travel Story
```
Emma boarded the train to London at Victoria Station. During the journey, she read a novel by Jane Austen 
and enjoyed the scenic countryside views. Upon arrival at King's Cross, she met her cousin James.
```
**Expected Objects:** Emma, train, London, Victoria Station, novel, Jane Austen, countryside, King's Cross, James
**Expected Relationships:** Emma-James (cousins), Emma-London (traveling to), etc.

## Complex Examples

### Example 5: Historical Narrative
```
Napoleon Bonaparte led the French army across the Alps in 1800 during the Italian campaign. 
General Massena commanded the advance guard while Marshal Murat led the cavalry charge at the Battle of Marengo. 
The victory secured French control over northern Italy and changed the course of European history.
```
**Expected Objects:** Napoleon Bonaparte, French army, Alps, Italian campaign, General Massena, Marshal Murat, Battle of Marengo, northern Italy, European history
**Expected Relationships:** Military hierarchy and historical connections

### Example 6: Scientific Discovery
```
Marie Curie worked tirelessly in her laboratory in Paris, studying radioactive elements alongside her husband Pierre. 
Their groundbreaking research on radium and polonium earned them the Nobel Prize in Physics in 1903, 
shared with Henri Becquerel who discovered radioactivity.
```
**Expected Objects:** Marie Curie, laboratory, Paris, Pierre Curie, radioactive elements, radium, polonium, Nobel Prize, Physics, Henri Becquerel, radioactivity
**Expected Relationships:** Professional and personal relationships in scientific context

## Edge Cases and Challenges

### Example 7: Ambiguous Names
```
The doctor examined the patient in room 205. After reviewing the X-rays, 
she recommended surgery. The nurse prepared the medication.
```
**Expected Behavior:** Should NOT create objects for "the doctor," "the patient," "she," "the nurse" as these are unnamed references

### Example 8: Mixed Content
```
John called his sister Mary to discuss the new iPhone release. 
Apple's CEO announced the features at the September event in Cupertino. 
The stock price rose 3% following the announcement.
```
**Expected Objects:** John, Mary, iPhone, Apple, CEO, September event, Cupertino, stock price
**Expected Relationships:** John-Mary (siblings), CEO-Apple (works for), etc.

### Example 9: Dialogue and Quotes
```
"I love this restaurant," said Jennifer to her date Michael. 
The waiter at Chez François recommended the wine pairing. 
"This Bordeaux pairs perfectly with the duck," he explained.
```
**Expected Objects:** Jennifer, Michael, restaurant, waiter, Chez François, wine pairing, Bordeaux, duck
**Expected Relationships:** Jennifer-Michael (dating), waiter-restaurant (works at)

## Progressive Testing

### Add Incrementally
Start with this text and add each section progressively to test object preservation:

**Base text:**
```
Alice works at the bookstore downtown.
```

**Add section 1:**
```
Bob visits the bookstore every Tuesday to browse the mystery section.
```

**Add section 2:**
```
The bookstore owner, Mrs. Chen, has run the shop for twenty years.
```

**Add section 3:**
```
During the summer, Alice and Bob organized a reading club that meets in the back room.
```

**Expected Behavior:** Objects should accumulate (Alice, Bob, bookstore, Mrs. Chen, reading club, back room) with relationships building over time.

## Error Testing

### Example 10: Empty/Minimal Content
```
Hello.
```
**Expected Behavior:** Should return few or no objects

### Example 11: Technical Content
```
The function returns a boolean value based on the input parameters. 
Error handling is implemented using try-catch blocks.
```
**Expected Behavior:** Should extract minimal narrative objects from technical text

### Example 12: List Format
```
Shopping list:
- Apples
- Bread  
- Milk
- Coffee
```
**Expected Behavior:** Should handle non-narrative text gracefully

## Performance Testing

### Example 13: Long Text
```
[Use the first few paragraphs of a long story or article]
The old mansion stood at the end of Elm Street, where it had weathered decades of storms and seasons. 
Margaret inherited the property from her great-aunt Violet, who had lived there alone for forty years. 
The house contained countless memories: family photographs in silver frames, 
antique furniture passed down through generations, and a library filled with first-edition novels.

When Margaret first walked through the front door, she was struck by the smell of lavender and old books. 
Her cousin Daniel had warned her about the house's reputation in the neighborhood, 
but she was determined to restore it to its former glory. 
The local contractor, Mr. Rodriguez, had given her an estimate for the renovation work needed.

As autumn arrived, Margaret began the restoration project. She hired a team of craftsmen 
to repair the Victorian-era windows and restore the hardwood floors. 
The garden, once Violet's pride and joy, required extensive work to bring back the roses and herb garden.
```
**Expected Behavior:** Should handle longer text efficiently and extract numerous objects with relationships

## Testing Instructions

1. **Start Fresh**: Clear any existing objects before testing each example
2. **Copy Exactly**: Use copy-paste to avoid typos that might affect results
3. **Wait for Processing**: Allow the 2-second debounce timer to complete
4. **Check Relationships**: Verify that relationships are correctly identified
5. **Test Incrementally**: Use progressive examples to test object preservation
6. **Note Edge Cases**: Document any unexpected behavior with ambiguous text

## Expected Test Results

For each example, verify:
- ✅ Named entities are correctly identified
- ✅ Unnamed references ("the man", "she") are ignored
- ✅ Relationships between objects are logical
- ✅ Descriptions are factual and based on the text
- ✅ Objects persist when adding new text incrementally
- ✅ No hallucinated objects that aren't in the source text