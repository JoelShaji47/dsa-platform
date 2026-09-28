import { Suspense } from "react";
import ProblemsClient from "./problems-client";

export const metadata = {
  title: "Problems — CodeQuest",
};

export default function ProblemsPage() {
  return (
    <Suspense>
      <ProblemsClient />
    </Suspense>
  );
}
