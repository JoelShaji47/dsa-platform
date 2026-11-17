import { snap, snapQueue, step, type BaseStep, type VisualizerEntry } from "../trace-types";

export type TwitterOp =
  | { kind: "post"; user: number; tweetId: number }
  | { kind: "follow"; follower: number; followee: number }
  | { kind: "unfollow"; follower: number; followee: number }
  | { kind: "newsfeed"; user: number };

export interface DesignTwitterInput {
  ops: TwitterOp[];
}

interface Tweet {
  id: number;
  time: number;
}

function positiveInt(token: string, label: string): number {
  const value = Number(token);
  if (!Number.isInteger(value) || value < 1) {
    throw new Error(`${label} must be a positive integer`);
  }
  return value;
}

function nonNegativeInt(token: string, label: string): number {
  const value = Number(token);
  if (!Number.isInteger(value) || value < 0) {
    throw new Error(`${label} must be a non-negative integer`);
  }
  return value;
}

export function parseDesignTwitter(raw: string): DesignTwitterInput {
  const parts = raw
    .split(/[,\n;]+/)
    .map((s) => s.trim())
    .filter(Boolean);
  if (parts.length === 0) {
    throw new Error("Enter ops like: post 1 5, follow 1 2, newsfeed 1");
  }
  if (parts.length > 12) throw new Error("Keep it to 12 ops so the trace stays readable");

  const ops: TwitterOp[] = parts.map((part) => {
    const tokens = part.split(/\s+/);
    const kind = tokens[0]?.toLowerCase();
    if (kind === "post" && tokens.length === 3) {
      return {
        kind: "post",
        user: positiveInt(tokens[1], "user"),
        tweetId: nonNegativeInt(tokens[2], "tweet id"),
      };
    }
    if ((kind === "follow" || kind === "unfollow") && tokens.length === 3) {
      return {
        kind,
        follower: positiveInt(tokens[1], "follower"),
        followee: positiveInt(tokens[2], "followee"),
      };
    }
    if (kind === "newsfeed" && tokens.length === 2) {
      return { kind: "newsfeed", user: positiveInt(tokens[1], "user") };
    }
    throw new Error(`Bad op '${part}' — use post U ID, follow A B, unfollow A B, or newsfeed U`);
  });
  return { ops };
}

export function generateDesignTwitter({ ops }: DesignTwitterInput): BaseStep[] {
  const steps: BaseStep[] = [];
  const tweets = new Map<number, Tweet[]>();
  const follows = new Map<number, Set<number>>();
  const output: number[][] = [];
  let clock = 0;

  const followeesOf = (user: number) =>
    [...(follows.get(user) ?? new Set<number>())].sort((a, b) => a - b);
  const tweetsOf = (user: number) => (tweets.get(user) ?? []).map((tweet) => tweet.id);
  const feedOf = (user: number) => {
    const authors = new Set<number>([user, ...followeesOf(user)]);
    const feed = [...authors].flatMap((author) => tweets.get(author) ?? []);
    feed.sort((a, b) => b.time - a.time);
    return feed.slice(0, 10).map((tweet) => tweet.id);
  };
  const queueSnap = (user: number, active: number[] = []) =>
    snapQueue(
      feedOf(user).map((id) => `#${id}`),
      { active, label: `newsfeed of user ${user} (newest first)` }
    );
  const first = ops[0];
  const firstUser = first == null ? 1 : "user" in first ? first.user : first.follower;

  steps.push(
    step(
      0,
      "Start",
      "Each user has posts and a follow set. A newsfeed merges the user's tweets with followees' tweets, newest first, capped at 10.",
      0,
      snap([]),
      {},
      { queue: queueSnap(firstUser) }
    )
  );

  for (const op of ops) {
    if (op.kind === "post") {
      const list = tweets.get(op.user) ?? [];
      list.push({ id: op.tweetId, time: clock });
      tweets.set(op.user, list);
      clock += 1;
      steps.push(
        step(
          steps.length,
          "Post",
          `User ${op.user} posts tweet ${op.tweetId}.`,
          1,
          snap(tweetsOf(op.user).map((id) => `t${id}`)),
          { user: op.user, tweet: op.tweetId },
          { queue: queueSnap(op.user) }
        )
      );
    } else if (op.kind === "follow") {
      const set = follows.get(op.follower) ?? new Set<number>();
      set.add(op.followee);
      follows.set(op.follower, set);
      steps.push(
        step(
          steps.length,
          "Follow",
          `User ${op.follower} follows user ${op.followee} — their tweets join the feed.`,
          2,
          snap(followeesOf(op.follower).map((user) => `u${user}`)),
          { follower: op.follower, followee: op.followee },
          { queue: queueSnap(op.follower) }
        )
      );
    } else if (op.kind === "unfollow") {
      const set = follows.get(op.follower) ?? new Set<number>();
      set.delete(op.followee);
      follows.set(op.follower, set);
      steps.push(
        step(
          steps.length,
          "Unfollow",
          `User ${op.follower} unfollows user ${op.followee} — their tweets leave the feed.`,
          2,
          snap(followeesOf(op.follower).map((user) => `u${user}`)),
          { follower: op.follower, followee: op.followee },
          { queue: queueSnap(op.follower) }
        )
      );
    } else {
      const feed = feedOf(op.user);
      output.push(feed);
      steps.push(
        step(
          steps.length,
          "Newsfeed",
          feed.length === 0
            ? `User ${op.user}'s feed is empty.`
            : `User ${op.user}'s 10 most recent tweets: ${feed.map((id) => `#${id}`).join(", ")}.`,
          3,
          snap(followeesOf(op.user).map((user) => `u${user}`)),
          { user: op.user, feed: feed.join(", ") },
          { queue: queueSnap(op.user, feed.length > 0 ? [0] : []) }
        )
      );
    }
  }

  const result = output
    .map((feed) => (feed.length > 0 ? feed.join(" ") : "(empty)"))
    .join(" | ");
  steps.push(
    step(
      steps.length,
      "Done",
      output.length === 0
        ? "No newsfeed calls, so there is no output."
        : `Newsfeed results: ${result}.`,
      4,
      snap([]),
      { calls: output.length },
      { queue: queueSnap(firstUser), result, done: true }
    )
  );
  return steps;
}

export const designTwitterEntry: VisualizerEntry = {
  slug: "design-twitter",
  title: "Design Twitter",
  inputHint: "post 1 5, post 2 6, newsfeed 1, follow 1 2, newsfeed 1",
  defaultInput:
    "post 1 5, post 2 6, newsfeed 1, follow 1 2, newsfeed 1, unfollow 1 2, newsfeed 1",
  presets: [
    {
      label: "Classic",
      value:
        "post 1 5, post 2 6, newsfeed 1, follow 1 2, newsfeed 1, unfollow 1 2, newsfeed 1",
    },
    { label: "Follow feed", value: "post 1 1, post 2 2, follow 1 2, newsfeed 1" },
    { label: "Solo", value: "post 1 1, newsfeed 1" },
  ],
  pseudocode: [
    "tweets = {}; follows = {}; time = 0",
    "post(u, id): tweets[u].append((id, time)); time += 1",
    "follow(a, b): follows[a].add(b)",
    "unfollow(a, b): follows[a].remove(b)",
    "newsfeed(u): merge tweets of u and follows[u] by time desc; return first 10",
  ],
  parse: (raw: string) => parseDesignTwitter(raw),
  generate: (input: unknown) => generateDesignTwitter(input as DesignTwitterInput),
};
