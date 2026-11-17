/** Small shared parsers for trace inputs. Seeded test cases mix bracket,
 * whitespace, count-prefixed and line-per-row formats, so every trace accepts
 * the format shown in its problem example. */

export function inputLines(raw: string): string[] {
  return raw
    .replace(/\r/g, "")
    .split("\n")
    .map((line) => line.trim())
    .filter((line) => line.length > 0);
}

export function tokenize(text: string): string[] {
  const bracket = text.match(/\[([^\]]*)\]/);
  const body = bracket ? bracket[1] : text;
  return body
    .split(/[\s,]+/)
    .map((token) => token.trim())
    .filter((token) => token.length > 0);
}

export function numbersFrom(text: string): number[] {
  return tokenize(text).map((token) => {
    const value = Number(token);
    if (!Number.isFinite(value)) throw new Error("Use numbers only");
    return value;
  });
}

export function integersFrom(text: string): number[] {
  const values = numbersFrom(text);
  if (values.some((value) => !Number.isInteger(value))) {
    throw new Error("Use integers only");
  }
  return values;
}

export function charTokensFrom(text: string): string[] {
  const bracket = text.match(/\[([^\]]*)\]/);
  if (bracket) {
    return bracket[1]
      .split(",")
      .map((token) => token.trim().replace(/^["']|["']$/g, ""))
      .filter((token) => token.length > 0);
  }
  return [...text.trim()];
}

/** Count-prefixed array, e.g. "4\n1 2 3 1", or a bracket array. */
export function countedNumbers(raw: string): { count: number; values: number[] } {
  const lines = inputLines(raw);
  if (lines.length === 0) throw new Error("Use a count followed by the array");
  const bracket = lines[0].match(/^\[/);
  if (bracket || lines.length === 1) {
    const values = integersFrom(lines[0]);
    return { count: values.length, values };
  }
  const count = Number(lines[0]);
  if (!Number.isInteger(count) || count < 0) {
    throw new Error("The first line must be a non-negative count");
  }
  const values = integersFrom(lines.slice(1).join(" "));
  if (values.length !== count) {
    throw new Error(`Expected ${count} values, received ${values.length}`);
  }
  return { count, values };
}

/** Count-prefixed lines, e.g. "3\neat\ntea\ntan". */
export function countedLines(raw: string, pattern?: RegExp): string[] {
  const lines = inputLines(raw);
  if (lines.length === 0) throw new Error("Use a count followed by values");
  const count = Number(lines[0]);
  if (!Number.isInteger(count) || count < 0) {
    throw new Error("The first line must be a non-negative count");
  }
  const values = lines.slice(1, count + 1);
  if (values.length !== count) {
    throw new Error(`Expected ${count} values, received ${values.length}`);
  }
  if (pattern && values.some((value) => !pattern.test(value))) {
    throw new Error("One or more values have an invalid format");
  }
  return values;
}

export function parseGrid(
  raw: string,
  options: {
    maxRows?: number;
    maxCols?: number;
    allowed?: RegExp;
    label?: string;
  } = {}
): { rows: number; cols: number; grid: string[][] } {
  const { maxRows = 8, maxCols = 8, allowed, label = "grid" } = options;
  const lines = inputLines(raw);
  if (lines.length < 2) throw new Error(`Use: R C, then R rows of ${label}`);

  const [rows, cols] = lines[0].split(/[\s,]+/).map(Number);
  if (!Number.isInteger(rows) || !Number.isInteger(cols) || rows < 1 || cols < 1) {
    throw new Error("Grid dimensions must be positive integers");
  }
  if (rows > maxRows || cols > maxCols) {
    throw new Error(`Keep the grid to ${maxRows}x${maxCols} so the trace stays readable`);
  }
  if (lines.length < rows + 1) throw new Error("The grid is missing rows");

  const grid = lines.slice(1, rows + 1).map((line) => {
    const compact =
      allowed && !line.includes(" ") && !line.includes(",") && line.length === cols;
    const cells = compact ? [...line] : line.split(/[\s,]+/);
    if (cells.length !== cols) {
      throw new Error(`Each row needs exactly ${cols} cells`);
    }
    if (allowed && cells.some((cell) => !allowed.test(cell))) {
      throw new Error(`Each cell must match ${allowed}`);
    }
    return cells;
  });

  return { rows, cols, grid };
}

export function parseIntGrid(
  raw: string,
  maxRows = 6,
  maxCols = 6
): { rows: number; cols: number; grid: number[][] } {
  const parsed = parseGrid(raw, {
    maxRows,
    maxCols,
    allowed: /^-?\d+$/,
    label: "integers",
  });
  return {
    rows: parsed.rows,
    cols: parsed.cols,
    grid: parsed.grid.map((row) => row.map(Number)),
  };
}

export function parseIntervals(raw: string): [number, number][] {
  const lines = inputLines(raw);
  if (lines.length === 0) throw new Error("Use: N, then N lines of start end");
  const count = Number(lines[0]);
  if (!Number.isInteger(count) || count < 1) throw new Error("The first line must be a count");
  if (lines.length < count + 1) throw new Error("Some interval lines are missing");
  const intervals = lines.slice(1, count + 1).map((line) => {
    const pair = integersFrom(line);
    if (pair.length !== 2) throw new Error("Each interval needs exactly two numbers");
    if (pair[0] > pair[1]) throw new Error("Each interval must have start <= end");
    return [pair[0], pair[1]] as [number, number];
  });
  return intervals;
}

export function formatNumberList(values: (number | string)[]): string {
  return values.join(" ");
}

export function formatMatrix(values: (number | string)[][]): string {
  return values.map((row) => row.join(" ")).join("\n");
}
