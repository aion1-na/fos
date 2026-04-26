import { PopulationInspector } from "@/components/population/PopulationInspector";
import { populationFixture } from "@/lib/population/fixture";

export default function PopulationPage() {
  return (
    <main className="workspace population-workspace" id="studio-main">
      <PopulationInspector population={populationFixture} />
    </main>
  );
}
