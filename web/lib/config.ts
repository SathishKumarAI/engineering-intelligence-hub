// Domain config — the only file that changes between the three projects.
export const siteConfig = {
  name: "Engineering Intelligence Hub",
  tagline:
    "Ask questions about your engineering docs (RFCs, runbooks, ADRs, API refs). Every answer cites the source.",
  accent: "#4f46e5", // indigo
  disclaimer:
    "Answers reflect the indexed docs — verify against the live system. Sample data is synthetic.",
  apiBaseUrl: process.env.NEXT_PUBLIC_API_BASE_URL ?? "http://localhost:8000",
  githubRepo:
    process.env.NEXT_PUBLIC_GITHUB_REPO ?? "SathishKumarAI/engineering-intelligence-hub",
  apiKey: process.env.NEXT_PUBLIC_API_KEY ?? "",
  examples: [
    "How do I roll back the most recent deploy?",
    "What is the default API rate limit?",
    "Which database is the primary datastore and why?",
    "How long are auth tokens valid?",
  ],
};
