import React, { useEffect, useRef, useState } from 'react';
import { FixedSizeList as List } from 'react-window';
import AutoSizer from 'react-virtualized-auto-sizer';
import InfiniteLoader from 'react-window-infinite-loader';
import { useTheme } from '../hooks/useTheme';

/**
 * VirtualizedChatList component for optimized rendering of long conversations
 * Addresses the medium-priority issue with performance degradation in long conversations
 * 
 * @param {Object} props Component props
 * @param {Array} props.messages Array of chat messages to display
 * @param {Function} props.loadMoreMessages Function to load more messages when scrolling up
 * @param {boolean} props.hasMoreMessages Whether there are more messages to load
 * @param {boolean} props.isLoadingMore Whether more messages are currently being loaded
 * @param {Function} props.renderMessage Function to render an individual message
 */
const VirtualizedChatList = ({
  messages,
  loadMoreMessages,
  hasMoreMessages = false,
  isLoadingMore = false,
  renderMessage,
}) => {
  const listRef = useRef(null);
  const infiniteLoaderRef = useRef(null);
  const [scrollToIndex, setScrollToIndex] = useState(null);
  const { theme } = useTheme();
  
  // Calculate estimated item size based on average message length
  const getEstimatedItemSize = () => {
    if (!messages.length) return 100;
    
    // Base height for message container
    const baseHeight = 60;
    
    // Estimate average characters per line
    const charsPerLine = 80;
    
    // Estimate line height
    const lineHeight = 24;
    
    // Calculate average message length
    const avgLength = messages.reduce((sum, msg) => sum + (msg.content?.length || 0), 0) / messages.length;
    
    // Estimate number of lines
    const estimatedLines = Math.ceil(avgLength / charsPerLine);
    
    // Calculate estimated height
    return baseHeight + (estimatedLines * lineHeight);
  };
  
  const estimatedItemSize = getEstimatedItemSize();
  
  // Total number of items (messages + loading item if needed)
  const itemCount = hasMoreMessages ? messages.length + 1 : messages.length;
  
  // Check if an item is loaded
  const isItemLoaded = (index) => {
    return !hasMoreMessages || index < messages.length;
  };
  
  // Load more items when scrolling to the top
  const loadMoreItems = isLoadingMore ? () => {} : loadMoreMessages;
  
  // Scroll to bottom on new messages
  useEffect(() => {
    if (listRef.current && messages.length > 0) {
      // Only auto-scroll if we're near the bottom already
      const list = listRef.current;
      
      // Check if we're at the bottom before scrolling
      if (list._outerRef.scrollTop + list._outerRef.clientHeight >= list._outerRef.scrollHeight - 200) {
        setScrollToIndex(messages.length - 1);
      }
    }
  }, [messages.length]);
  
  // Reset scroll position when scrollToIndex changes
  useEffect(() => {
    if (scrollToIndex !== null && listRef.current) {
      listRef.current.scrollToItem(scrollToIndex, 'end');
      setScrollToIndex(null);
    }
  }, [scrollToIndex]);
  
  // Render a message item
  const MessageItem = ({ index, style }) => {
    // Render loading indicator for the first item if loading more
    if (!isItemLoaded(index)) {
      return (
        <div 
          style={{
            ...style,
            display: 'flex',
            alignItems: 'center',
            justifyContent: 'center',
            padding: '10px'
          }}
        >
          <div className="loading-spinner" />
        </div>
      );
    }
    
    // Render actual message
    const message = messages[index];
    return (
      <div style={style}>
        {renderMessage(message, index)}
      </div>
    );
  };
  
  return (
    <div 
      style={{ 
        height: '100%', 
        width: '100%',
        backgroundColor: theme === 'dark' ? '#1a1a1a' : '#ffffff'
      }}
    >
      <AutoSizer>
        {({ height, width }) => (
          <InfiniteLoader
            ref={infiniteLoaderRef}
            isItemLoaded={isItemLoaded}
            itemCount={itemCount}
            loadMoreItems={loadMoreItems}
            threshold={5}
          >
            {({ onItemsRendered, ref }) => (
              <List
                ref={(list) => {
                  ref(list);
                  listRef.current = list;
                }}
                height={height}
                width={width}
                itemCount={itemCount}
                itemSize={estimatedItemSize}
                onItemsRendered={onItemsRendered}
                overscanCount={5}
                // Invert the list to have newest messages at the bottom
                // and enable infinite scrolling upward
                style={{
                  paddingTop: 10,
                  paddingBottom: 10
                }}
              >
                {MessageItem}
              </List>
            )}
          </InfiniteLoader>
        )}
      </AutoSizer>
    </div>
  );
};

export default VirtualizedChatList;
