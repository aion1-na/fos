import type { Metadata } from "next";

import "./styles.css";

export const metadata: Metadata = {
  title: "FOS Atlas",
  description: "Dataset directory for the FOS data workstream",
};

export default function RootLayout({
  children,
}: Readonly<{
  children: React.ReactNode;
}>) {
  return (
    <html lang="en">
      <body>{children}</body>
    </html>
  );
}
