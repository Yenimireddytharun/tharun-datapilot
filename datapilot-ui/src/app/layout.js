import "./globals.css";

export const metadata = {
  title: "DataPilot",
  description: "Data Analysis Dashboard",
};

export default function RootLayout({ children }) {
  return (
    <html lang="en">
      <body>{children}</body>
    </html>
  );
}