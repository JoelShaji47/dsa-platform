import type { Metadata } from "next";
import LeaguesClient from "./leagues-client";

export const metadata: Metadata = {
  title: "Leagues — CodeQuest",
};

export default function LeaguesPage() {
  return <LeaguesClient />;
}
