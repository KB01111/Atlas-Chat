import type { ColumnDef } from '@tanstack/react-table';
import type { TFile } from 'librechat-data-provider';
import { ArrowUpDown } from 'lucide-react';

import { Button } from '~/components/ui';
import useLocalize from '~/hooks/useLocalize';
import { formatDate } from '~/utils';

import PanelFileCell from './PanelFileCell';

// Define headers outside the main array to use hooks
const FileNameHeader = ({ column }: { column: any }) => {
  const localize = useLocalize();
  return (
    <Button
      variant="ghost"
      className="hover:bg-surface-hover"
      onClick={() => column.toggleSorting(column.getIsSorted() === 'asc')}
    >
      {localize('com_ui_name')}
      <ArrowUpDown className="ml-2 h-4 w-4" />
    </Button>
  );
};

const DateHeader = ({ column }: { column: any }) => {
  const localize = useLocalize();
  return (
    <Button
      variant="ghost"
      className="hover:bg-surface-hover"
      onClick={() => column.toggleSorting(column.getIsSorted() === 'asc')}
    >
      {localize('com_ui_date')}
      <ArrowUpDown className="ml-2 h-4 w-4" />
    </Button>
  );
};

export const columns: ColumnDef<TFile | undefined>[] = [
  {
    accessorKey: 'filename',
    header: FileNameHeader,
    meta: {
      size: '150px',
    },
    cell: ({ row }) => <PanelFileCell row={row} />,
  },
  {
    accessorKey: 'updatedAt',
    meta: {
      size: '10%',
    },
    header: DateHeader,
    cell: ({ row }) => (
      <span className="flex justify-end text-xs">
        {formatDate(row.original?.updatedAt?.toString() ?? '')}
      </span>
    ),
  },
];
