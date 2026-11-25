import { defineConfig } from "vite";
import react from "@vitejs/plugin-react";
import tailwindcss from "@tailwindcss/vite";

export default defineConfig(({ mode }) => {
  const housing = mode === "local-housing";
  const local = mode === "engine" || housing;
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
            const path = id.replaceAll("\\", "/");
            if (/\/src\/(?:App\.tsx|(?:fixtures|atlas|navigation|navigation_data)\.ts|components\/OpportunityInteraction|gameplay\/interaction\/)|\/src\/gameplay\/(preview|GameplayProvider|EngineProvider)\.tsx?$/.test(path)) {
              this.error(`Preview-only module entered local bundle: ${id}`);
            }
            if (!housing && /\/src\/(?:housing-main\.tsx|components\/HousingPanel\.tsx|gameplay\/(?:housing|housingHost|outbox)\.ts)$/.test(path)) {
              this.error(`Housing-only module entered the read-only inspection bundle: ${id}`);
            }
          }
        }
      },
    }],
    build: {
      outDir: housing ? "dist/housing" : local ? "dist/local" : "dist/preview",
      assetsDir: "assets",
      assetsInlineLimit: 0,
      sourcemap: false,
      manifest: false,
      rollupOptions: {
        input: housing ? "housing.html" : local ? "local.html" : "index.html",
        output: {
          entryFileNames: "assets/[name]-[hash].js",
          chunkFileNames: "assets/[name]-[hash].js",
          assetFileNames: "assets/[name]-[hash][extname]",
        },
      },
    },
  };
});
