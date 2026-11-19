import { defineConfig } from "vite";
import react from "@vitejs/plugin-react";
import tailwindcss from "@tailwindcss/vite";

export default defineConfig(({ mode }) => {
  const local = mode === "engine";
  return {
    base: "/",
    publicDir: false,
    plugins: [react(), tailwindcss(), {
      name: "local-runtime-boundary",
      generateBundle(_, bundle) {
        if (!local) return;
        for (const output of Object.values(bundle)) {
          if (output.type !== "chunk") continue;
          for (const id of Object.keys(output.modules)) {
            if (/\/src\/(fixtures|atlas|navigation|navigation_data)\.ts$|\/src\/gameplay\/(preview|GameplayProvider|EngineProvider)\.tsx?$/.test(id.replaceAll("\\", "/"))) {
              this.error(`Preview-only module entered local bundle: ${id}`);
            }
          }
        }
      },
    }],
    build: {
      outDir: local ? "dist/local" : "dist/preview",
      assetsDir: "assets",
      assetsInlineLimit: 0,
      sourcemap: false,
      manifest: false,
      rollupOptions: {
        input: local ? "local.html" : "index.html",
        output: {
          entryFileNames: "assets/[name]-[hash].js",
          chunkFileNames: "assets/[name]-[hash].js",
          assetFileNames: "assets/[name]-[hash][extname]",
        },
      },
    },
  };
});
