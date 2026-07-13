import { describe, expect, it } from "vitest";
import {
  AXIS_NAMES,
  axesFromBits,
  glyphGeometry,
  permutationBits,
  permutationLabel,
  quantizedBits
} from "./character";

describe("character permutation matrix", () => {
  it("uses the same 2/4 axis values that are applied on selection", () => {
    for (let index = 0; index < 64; index += 1) {
      const bits = permutationBits(index);
      const matrixAxes = axesFromBits(bits);
      expect(AXIS_NAMES.map((name) => matrixAxes[name])).toEqual(
        bits.map((bit) => (bit ? 4 : 2))
      );
      expect(quantizedBits(matrixAxes)).toEqual(bits);
      expect(glyphGeometry({ ...matrixAxes })).toEqual(glyphGeometry(matrixAxes));
    }
  });

  it("keeps the two main modules separated across all permutations", () => {
    for (let index = 0; index < 64; index += 1) {
      const geometry = glyphGeometry(axesFromBits(permutationBits(index)));
      const gap = geometry.right.x - (geometry.left.x + geometry.left.width);
      expect(gap).toBeGreaterThan(5);
      expect(geometry.bridge.width).toBeGreaterThan(4);
      expect(geometry.left.x).toBeGreaterThanOrEqual(8);
      expect(geometry.right.x + geometry.right.width).toBeLessThanOrEqual(56);
    }
  });

  it("produces all 64 bit combinations", () => {
    const keys = new Set(Array.from({ length: 64 }, (_, index) => permutationBits(index).join("")));
    expect(keys.size).toBe(64);
  });

  it("names the selectable 2/4 landmarks rather than the unreachable 1/5 extremes", () => {
    expect(permutationLabel([0, 0, 0, 0, 0, 0])).toBe(
      "spare · soft · calm · restrained · open · recognizable"
    );
    expect(permutationLabel([1, 1, 1, 1, 1, 1])).toBe(
      "detailed · geometric · active · friendly · compact · distinctive"
    );
  });
});
