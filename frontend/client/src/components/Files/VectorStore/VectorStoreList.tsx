import React from 'react';
import VectorStoreListItem from './VectorStoreListItem';
import { TVectorStore } from '~/common';

type VectorStoreListProps = {
  vectorStores: TVectorStore[];
  deleteVectorStore: (id: string | undefined) => void;
};

export default function VectorStoreList({ vectorStores, deleteVectorStore }: VectorStoreListProps) {
  return (
    <div>
      {vectorStores.map((vectorStore: TVectorStore, index: number) => (
        <VectorStoreListItem
          key={index}
          vectorStore={vectorStore}
          deleteVectorStore={deleteVectorStore}
        />
      ))}
    </div>
  );
}
