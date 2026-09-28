import { redirect } from "next/navigation";

export default async function ProblemSlugPage({
  params,
}: {
  params: Promise<{ slug: string }>;
}) {
  const { slug } = await params;
  redirect(`/problems/${slug}/solve`);
}
