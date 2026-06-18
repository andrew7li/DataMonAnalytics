import "./CardTile.css";

export type CardTileData = {
  name: string;
  set: string;
  price: number;
  psaGrade: number;
  changePct: number;
  image: string;
};

function formatPrice(price: number) {
  return new Intl.NumberFormat("en-US", {
    style: "currency",
    currency: "USD",
    maximumFractionDigits: 0,
  }).format(price);
}

export default function CardTile({
  name,
  set,
  price,
  psaGrade,
  changePct,
  image,
}: CardTileData) {
  const isUp = changePct >= 0;

  return (
    <div className="card-tile">
      <img className="card-tile-art" src={image} alt={name} />
      <div className="card-tile-body">
        <div className="card-tile-name">{name}</div>
        <div className="card-tile-set">{set}</div>
        <div className="card-tile-meta">
          <span className="card-tile-price">{formatPrice(price)}</span>
          <span className="card-tile-psa">PSA {psaGrade}</span>
        </div>
        <span className={`card-tile-change ${isUp ? "up" : "down"}`}>
          <svg
            viewBox="0 0 24 24"
            fill="none"
            stroke="currentColor"
            strokeWidth="2"
            strokeLinecap="round"
            strokeLinejoin="round"
            aria-hidden="true"
          >
            {isUp ? (
              <polyline points="3 17 9 11 13 15 21 7" />
            ) : (
              <polyline points="3 7 9 13 13 9 21 17" />
            )}
          </svg>
          {isUp ? "+" : ""}
          {changePct.toFixed(1)}%
        </span>
      </div>
    </div>
  );
}
