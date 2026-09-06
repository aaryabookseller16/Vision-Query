const aliases = {
  animal: ["animal", "dog", "pet"], architecture: ["architecture", "building", "buildings", "city", "interior"],
  beverage: ["beverage", "coffee", "drink", "latte"], breakfast: ["breakfast", "coffee", "egg", "food", "toast"],
  calm: ["calm", "peaceful", "quiet", "still"], canine: ["canine", "dog", "pet"], downtown: ["downtown", "city", "skyline", "urban"],
  evening: ["evening", "night", "sunset", "blue hour"], hiking: ["hiking", "forest", "mountain", "path", "trail"],
  landscape: ["landscape", "desert", "forest", "lake", "mountain", "nature"], people: ["people", "person", "portrait", "woman"],
  puppy: ["puppy", "dog", "pet"], room: ["room", "interior", "office", "workspace"], scenic: ["scenic", "landscape", "nature"],
  work: ["work", "business", "office", "workspace"],
};
const stopWords = new Set(["a", "an", "and", "at", "in", "of", "on", "the", "to", "with"]);

export function tokenize(value) {
  return value.toLowerCase().normalize("NFKD").replace(/[^a-z0-9\s-]/g, " ").split(/\s+/)
    .map((token) => token.trim()).filter((token) => token && !stopWords.has(token));
}

function expandedTerms(query) {
  const tokens = tokenize(query);
  const terms = new Set(tokens);
  tokens.forEach((token) => {
    if (token.endsWith("s") && token.length > 3) terms.add(token.slice(0, -1));
    (aliases[token] || []).forEach((alias) => terms.add(alias));
  });
  return { tokens, terms: [...terms] };
}

export function scoreImage(image, query) {
  const { tokens, terms } = expandedTerms(query);
  if (!tokens.length) return 0;
  const title = image.title.toLowerCase();
  const description = image.description.toLowerCase();
  const tags = image.tags.map((tag) => tag.toLowerCase());
  let matchedTokens = 0;
  let weightedScore = 0;
  tokens.forEach((token) => {
    const related = new Set([token, ...(aliases[token] || [])]);
    if ([...related].some((term) => tags.some((tag) => tag === term || tag.includes(term) || term.includes(tag)))) matchedTokens += 1;
  });
  terms.forEach((term) => {
    if (tags.includes(term)) weightedScore += 1.2;
    else if (tags.some((tag) => tag.includes(term) || term.includes(tag))) weightedScore += 0.75;
    if (title.includes(term)) weightedScore += 0.55;
    if (description.includes(term)) weightedScore += 0.25;
  });
  if (!matchedTokens && weightedScore === 0) return 0;
  return Math.min(0.99, 0.38 + (matchedTokens / tokens.length) * 0.42 + Math.min(weightedScore, 3) * 0.06);
}

export function rankImages(images, query, category = "All") {
  const candidates = category === "All" ? images : images.filter((image) => image.category === category);
  if (!query.trim()) return candidates.map((image) => ({ ...image, score: null }));
  return candidates.map((image) => ({ ...image, score: scoreImage(image, query) }))
    .filter((image) => image.score > 0).sort((a, b) => b.score - a.score || a.title.localeCompare(b.title));
}
