import { Suspense } from "react";
import SqlSolveClient from "./solve-client";

export default function SqlSolvePage() {
  return (
    <Suspense>
      <SqlSolveClient />
    </Suspense>
  );
}
