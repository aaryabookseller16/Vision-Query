import { describe, expect, it } from "vitest";
import { catalog } from "./catalog.js";
import { rankImages, tokenize } from "./search.js";

describe("semantic demo search", () => {
  it("normalizes punctuation and removes filler words", () => expect(tokenize("A dog, on the trail!")).toEqual(["dog", "trail"]));
  it("ranks direct concepts first", () => {
    expect(rankImages(catalog, "quiet alpine lake")[0].id).toBe("alpine-lake");
    expect(rankImages(catalog, "modern office with sunlight")[0].id).toBe("sunlit-office");
  });
  it("understands a small synonym set", () => expect(rankImages(catalog, "playful puppy")[0].id).toBe("curious-dog"));
  it("honors category filters", () => expect(rankImages(catalog, "green", "Food").every((image) => image.category === "Food")).toBe(true));
  it("returns an intentional empty state", () => expect(rankImages(catalog, "spaceship astronaut")).toEqual([]));
});
