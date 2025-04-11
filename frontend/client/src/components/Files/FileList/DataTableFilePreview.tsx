import React from 'react';

import { TVectorStore } from '~/common';

import { fileTableColumns } from './../FileList/FileTableColumns';
import DataTableFile from './DataTableFile';
import { files } from '../../Chat/Input/Files/Table';

const vectorStoresAttached: TVectorStore[] = [
  {
    name: 'vector 1 vector 1',
    created_at: '2022-01-01T10:00:00',
    _id: 'id',
    object: 'vector_store',
  },
  {
    name: 'vector 1 vector 1',
    created_at: '2022-01-01T10:00:00',
    _id: 'id',
    object: 'vector_store',
  },
  {
    name: 'vector 1 vector 1',
    created_at: '2022-01-01T10:00:00',
    _id: 'id',
    object: 'vector_store',
  },
  {
    name: 'vector 1 vector 1',
    created_at: '2022-01-01T10:00:00',
    _id: 'id',
    object: 'vector_store',
  },
  {
    name: 'vector 1 vector 1',
    created_at: '2022-01-01T10:00:00',
    _id: 'id',
    object: 'vector_store',
  },
  {
    name: 'vector 1 vector 1',
    created_at: '2022-01-01T10:00:00',
    _id: 'id',
    object: 'vector_store',
  },
  {
    name: 'vector 1 vector 1',
    created_at: '2022-01-01T10:00:00',
    _id: 'id',
    object: 'vector_store',
  },
  {
    name: 'vector 1 vector 1',
    created_at: '2022-01-01T10:00:00',
    _id: 'id',
    object: 'vector_store',
  },
  {
    name: 'vector 1 vector 1',
    created_at: '2022-01-01T10:00:00',
    _id: 'id',
    object: 'vector_store',
  },
  {
    name: 'vector 1 vector 1',
    created_at: '2022-01-01T10:00:00',
    _id: 'id',
    object: 'vector_store',
  },
];

files.forEach((file) => {
  file['vectorsAttached'] = vectorStoresAttached;
});

export default function DataTableFilePreview() {
  return (
    <div>
      <DataTableFile columns={fileTableColumns} data={files} />
      <div className="mt-5 sm:mt-4" />
    </div>
  );
}
