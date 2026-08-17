import logoUrl from '../assets/logo-lekha-likhi.png';

export default function Logo({ className }) {
  return (
    <img
      src={logoUrl}
      alt="Lekha Likhi"
      className={className}
      decoding="async"
    />
  );
}
