import { trpc } from "..";
import angrySquirtle from "../../assets/angry-squirtle.jpg";

export default function UploadPage() {
  const userQuery = trpc.userById.useQuery("1");

  if (userQuery.isLoading) return <div>Loading...</div>;
  if (userQuery.error) return <div>Error: {userQuery.error.message}</div>;

  return (
    <div>
      <h1>Sup Boys I am andrew</h1>
      <img src={angrySquirtle} alt="Angry Squirtle" />
      <div>Hit backend: {userQuery.data?.name}</div>
    </div>
  );
}
