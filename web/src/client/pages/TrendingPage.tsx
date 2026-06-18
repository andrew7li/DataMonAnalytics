import CardTile, { type CardTileData } from "../components/CardTile";
import angrySquirtle from "../../assets/angry-squirtle.jpg";
import "./TrendingPage.css";

const topPerformers: CardTileData[] = [
  { name: "Charizard", set: "Base Set", price: 4250, psaGrade: 10, changePct: 18.4, image: angrySquirtle },
  { name: "Blastoise", set: "Base Set", price: 1340, psaGrade: 9, changePct: 14.2, image: angrySquirtle },
  { name: "Venusaur", set: "Base Set", price: 980, psaGrade: 10, changePct: 11.6, image: angrySquirtle },
  { name: "Umbreon", set: "Neo Discovery", price: 760, psaGrade: 9, changePct: 9.8, image: angrySquirtle },
  { name: "Mewtwo", set: "Base Set", price: 540, psaGrade: 10, changePct: 7.3, image: angrySquirtle },
  { name: "Gengar", set: "Fossil", price: 410, psaGrade: 9, changePct: 5.1, image: angrySquirtle },
];

const worstPerformers: CardTileData[] = [
  { name: "Pikachu", set: "Base Set", price: 210, psaGrade: 8, changePct: -14.2, image: angrySquirtle },
  { name: "Snorlax", set: "Jungle", price: 180, psaGrade: 9, changePct: -11.5, image: angrySquirtle },
  { name: "Gyarados", set: "Base Set", price: 620, psaGrade: 9, changePct: -9.4, image: angrySquirtle },
  { name: "Dragonite", set: "Fossil", price: 340, psaGrade: 8, changePct: -7.8, image: angrySquirtle },
  { name: "Mew", set: "Promo", price: 295, psaGrade: 9, changePct: -6.2, image: angrySquirtle },
  { name: "Lugia", set: "Neo Genesis", price: 1850, psaGrade: 9, changePct: -4.9, image: angrySquirtle },
];

export default function TrendingPage() {
  return (
    <div className="trending-page">
      <header className="trending-header">
        <h1>Trending</h1>
        <p>Daily movers across the market, based on PSA-graded sales.</p>
      </header>

      <section className="trending-section">
        <h2 className="trending-section-title up">Top Performers Today</h2>
        <div className="card-gallery">
          {topPerformers.map((card) => (
            <CardTile key={card.name} {...card} />
          ))}
        </div>
      </section>

      <section className="trending-section">
        <h2 className="trending-section-title down">Worst Performers Today</h2>
        <div className="card-gallery">
          {worstPerformers.map((card) => (
            <CardTile key={card.name} {...card} />
          ))}
        </div>
      </section>
    </div>
  );
}
