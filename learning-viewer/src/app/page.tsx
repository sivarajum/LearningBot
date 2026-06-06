import Explorer from '@/components/Explorer';
import { getContentTree } from '@/lib/content-tree';

export default async function Home() {
  const tree = await getContentTree();
  return <Explorer initialTree={tree} />;
}
