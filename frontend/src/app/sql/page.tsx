import { Suspense } from "react";
import SqlProblemsClient from "./sql-client";

export const metadata = {
  title: "SQL Problems — CodeQuest",
};

export default function SqlProblemsPage() {
  return (
    <Suspense>
      <SqlProblemsClient />
    </Suspense>
  );
}
