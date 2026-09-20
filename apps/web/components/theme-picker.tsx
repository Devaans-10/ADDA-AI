"use client";

import { useEffect, useState } from "react";

type Theme = "light" | "dark" | "green" | "blue";
const themes: Theme[] = ["light", "dark", "green", "blue"];

export default function ThemePicker() {
  const [theme, setTheme] = useState<Theme>("light");

  useEffect(() => {
    const saved = window.localStorage.getItem("adda-theme");
    if (themes.includes(saved as Theme)) {
      setTheme(saved as Theme);
      window.document.documentElement.dataset.theme = saved as Theme;
    }
  }, []);

  function changeTheme(next: Theme) {
    setTheme(next);
    window.document.documentElement.dataset.theme = next;
    window.localStorage.setItem("adda-theme", next);
  }

  return <label className="theme-control"><span>Theme</span><select aria-label="Theme" value={theme} onChange={(event) => changeTheme(event.target.value as Theme)}>{themes.map((item) => <option key={item} value={item}>{item[0].toUpperCase() + item.slice(1)}</option>)}</select></label>;
}
