import type { Metadata } from "next";
import "./globals.css";

export const metadata: Metadata = {
  title: "NexusAI · Agent workspace",
  description: "One workspace for specialized AI agents, with a clear record of every task.",
};

export default function RootLayout({ children }: Readonly<{ children: React.ReactNode }>) {
  return <html lang="en"><body>{children}</body></html>;
}
