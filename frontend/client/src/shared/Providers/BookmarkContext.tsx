import { createContext, useContext } from 'react';

type TBookmarkContext = { bookmarks: any[] };

export const BookmarkContext = createContext<TBookmarkContext>({
  bookmarks: [],
} as TBookmarkContext);
export const useBookmarkContext = () => useContext(BookmarkContext);
