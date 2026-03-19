# Structural Patterns to Avoid - English

> Sentence and paragraph patterns that signal AI-generated text

## 1. Uniform Sentence Length

**Problem**: AI produces sentences in a narrow 15-25 word band.

**Solution**: Mix very short (3-5 words) with long sentences (25+ words). Never write 3+ consecutive sentences of similar length.

**Bad**:
> The festival showcases local traditions. Visitors can enjoy various activities. The event has grown significantly.

**Good**:
> The festival runs three days. By the second afternoon, most visitors have found their favorite stall and returned to it twice. The goat cheese sells out.

## 2. Rule of Three Compulsion

**Problem**: AI defaults to listing things in groups of exactly three.

**Solution**: List two, four, or five items. Never default to three.

**Bad**:
> The city offers great food, vibrant culture, and stunning architecture.

**Good**:
> The city offers great food and stunning architecture.
> The city offers great food, vibrant culture, stunning architecture, and easy transit.

## 3. Negative Parallelisms

**Problem**: "Not only X, but also Y" is a recognizable AI signature.

**Never write**:
- "It's not just X, it's Y"
- "Not only X, but also Y"
- "It's not about X, it's about Y"

**Solution**: State what something IS directly.

**Bad**:
> This isn't just a restaurant, it's an experience.

**Good**:
> The restaurant serves food you remember weeks later.

## 4. False Ranges

**Problem**: "From X to Y" as vague figurative spectrum.

**Never use for figurative ranges**:
- "from intimate gatherings to global movements"
- "from beginners to experts"

**Allowed for actual ranges**:
- "from 10 to 20 participants"
- "from January to March"

## 5. Participial Tack-Ons

**Problem**: -ing clauses at sentence ends are the most recognizable AI pattern.

**Never end with**:
- ", highlighting the importance of..."
- ", underscoring the significance of..."
- ", symbolizing the region's commitment to..."

**Solution**: Delete if it adds nothing. Make it a separate sentence if it matters.

## 6. Formulaic Conclusions

**Problem**: AI always wraps up with predictable structure.

**Never include**:
- "Challenges and Future Prospects" section
- "Despite its [positives], [subject] faces challenges..."
- Speculative "Future Outlook" paragraphs
- Vague optimism about "ongoing initiatives"

## 7. Compulsive Summaries

**Problem**: AI restates everything at the end.

**Never start paragraphs with**:
- "Overall,"
- "In conclusion,"
- "In summary,"
- "To recap"

**Solution**: If a conclusion is needed, make it say something new.

## 8. Metronomic Paragraph Rhythm

**Problem**: AI writes 3-4 sentence paragraphs consistently.

**Solution**:
- Use one-sentence paragraphs for emphasis
- Use longer paragraphs for sustained argument
- Vary paragraph lengths throughout

## 9. Vertical Lists with Bold Headers

**Problem**: Bullet lists with bold headers followed by colons.

**Bad**:
- **Performance**: The system is fast.
- **Reliability**: The system is stable.

**Good**:
- The system responds in under 100ms.
- Uptime has exceeded 99.9% for six months.

## 10. Em Dash Overuse

**Problem**: The em dash (—) has become "the ChatGPT dash."

**Rule**: One em dash per 500 words maximum.

**Solution**: Use periods, commas, or parentheses instead.

## 11. Declarative-Only Sentences

**Problem**: AI writes almost exclusively in declarative sentences.

**Solution**: Mix in:
- Questions: "Why does this matter?"
- Imperatives: "Think about that."
- Fragments: "Not ideal."

## 12. Predictable Paragraph Openings

**Problem**: AI opens every paragraph with its thesis sentence.

**Solution**: Start some paragraphs mid-thought — with a specific detail, scene, or example.

## 13. Uniform Syntactic Depth

**Problem**: AI produces medium-depth sentences with boring consistency.

**Solution**: Mix shallow and deep structures:
- Shallow: subject-verb-object, one clause
- Deep: multiple embeddings, subordinate clauses, parenthetical asides

## 14. Staccato Triplets

**Never write**:
> No meetings. No bureaucracy. Just results.

This is a recognized AI social media pattern.

## 15. Semicolon Overuse

**Problem**: AI deploys semicolons frequently for balanced compound sentences.

**Rule**: In non-academic prose, prefer periods or coordinating conjunctions.

## 16. Register Uniformity

**Problem**: AI maintains a single consistent register throughout.

**Solution**: Include 2-3 register shifts per piece:
- A casual parenthetical in formal prose
- A technical term in conversational writing
- A blunt colloquialism after careful analysis

## Detection Metrics

AI detectors use three main metrics:

1. **Perplexity**: How unpredictable word choices are
   - AI: ~21.2 (low - smooth, unsurprising)
   - Human: ~35.9 (high - varied, surprising)

2. **Burstiness**: Variation in sentence length/structure
   - AI: Low (sentences cluster 15-25 words)
   - Human: High (mixes 3-word and 35-word sentences)
   - Introducing burstiness reduced detection by up to 40%

3. **Stylometry**: Statistical fingerprint
   - Turnitin 2025+ analyzes 31 linguistic features
   - Focuses on "rhythm, flow, and predictability across entire paragraphs"