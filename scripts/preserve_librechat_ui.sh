#!/bin/bash

# Script to preserve LibreChat UI components for future use in Atlas-Chat
# This script identifies, backs up, and organizes LibreChat UI components

echo "Starting LibreChat UI preservation process..."

# Create a preservation directory
PRESERVATION_DIR="./librechat_ui_components"
mkdir -p $PRESERVATION_DIR

echo "Created preservation directory: $PRESERVATION_DIR"

# Function to copy a component to the preservation directory
preserve_component() {
        local source=$1
        local target="$PRESERVATION_DIR/$(dirname $source)"

        mkdir -p "$target"
        cp -r "$source" "$target/"

        echo "Preserved: $source"
}

# Function to create a component manifest
create_manifest() {
        local manifest="$PRESERVATION_DIR/manifest.json"
        local components=()

        # Find all preserved components
        while IFS= read -r file; do
                if [[ $file == *.jsx || $file == *.tsx || $file == *.js || $file == *.ts ]]; then
                        components+=("$(realpath --relative-to=$PRESERVATION_DIR $file)")
                fi
        done < <(find $PRESERVATION_DIR -type f | sort)

        # Create JSON manifest
        echo "{" >$manifest
        echo '  "name": "LibreChat UI Components",' >>$manifest
        echo '  "description": "Preserved UI components from LibreChat for potential future use in Atlas-Chat",' >>$manifest
        echo "  \"date\": \"$(date +%Y-%m-%d)\"," >>$manifest
        echo '  "components": [' >>$manifest

        for ((i = 0; i < ${#components[@]}; i++)); do
                echo "    \"${components[$i]}\"$(if [[ $i -lt $((${#components[@]} - 1)) ]]; then echo ","; fi)" >>$manifest
        done

        echo "  ]" >>$manifest
        echo "}" >>$manifest

        echo "Created component manifest: $manifest"
}

# Function to preserve valuable UI components
preserve_ui_components() {
        echo "Preserving valuable LibreChat UI components..."

        # Define the source directory for LibreChat components
        FRONTEND_DIR="./frontend/client/src"

        # List of valuable LibreChat UI components to preserve
        VALUABLE_COMPONENTS=(
                # Chat components
                "components/Chat/ChatMessage"
                "components/Chat/Messages"
                "components/Chat/Input"
                "components/Chat/Conversation"
                "components/Chat/ChatBar"
                "components/Chat/Markdown"
                "components/Chat/CodeBlock"

                # UI components
                "components/UI/Dropdown"
                "components/UI/Modal"
                "components/UI/Tooltip"
                "components/UI/Popover"
                "components/UI/Button"
                "components/UI/Card"
                "components/UI/Avatar"
                "components/UI/Icons"

                # Settings components
                "components/Settings/SettingsDialog"
                "components/Settings/SettingsOption"
                "components/Settings/ThemeSelector"

                # Auth components
                "components/Auth/Login"
                "components/Auth/Register"
                "components/Auth/ForgotPassword"

                # Layout components
                "components/Layout/Sidebar"
                "components/Layout/Header"
                "components/Layout/Footer"
                "components/Layout/Main"

                # Utility functions
                "utils/markdown"
                "utils/theme"
                "utils/storage"
                "utils/auth"
                "utils/chat"

                # Hooks
                "hooks/useLocalStorage"
                "hooks/useMediaQuery"
                "hooks/useDebounce"
                "hooks/useTheme"
        )

        # Preserve each component
        for component in "${VALUABLE_COMPONENTS[@]}"; do
                component_path="$FRONTEND_DIR/$component"

                # Check if it's a directory or file
                if [ -d "$component_path" ]; then
                        # Preserve the entire directory
                        preserve_component "$component_path"
                elif [ -f "$component_path.jsx" ]; then
                        preserve_component "$component_path.jsx"
                elif [ -f "$component_path.tsx" ]; then
                        preserve_component "$component_path.tsx"
                elif [ -f "$component_path.js" ]; then
                        preserve_component "$component_path.js"
                elif [ -f "$component_path.ts" ]; then
                        preserve_component "$component_path.ts"
                else
                        # Try to find files that match the pattern
                        find "$FRONTEND_DIR" -path "*$component*" -name "*.jsx" -o -name "*.tsx" -o -name "*.js" -o -name "*.ts" | while read file; do
                                preserve_component "$file"
                        done
                fi
        done
}

# Function to preserve styles
preserve_styles() {
        echo "Preserving LibreChat styles..."

        # Define the source directory for styles
        STYLES_DIR="./frontend/client/src/styles"

        # Create styles directory in preservation directory
        mkdir -p "$PRESERVATION_DIR/styles"

        # Copy all CSS and SCSS files
        find "$STYLES_DIR" -name "*.css" -o -name "*.scss" | while read file; do
                preserve_component "$file"
        done

        # Copy Tailwind configuration
        if [ -f "./frontend/client/tailwind.config.js" ]; then
                preserve_component "./frontend/client/tailwind.config.js"
        fi
}

# Function to preserve theme configurations
preserve_themes() {
        echo "Preserving LibreChat themes..."

        # Define the source directory for themes
        THEMES_DIR="./frontend/client/src/themes"

        # Check if themes directory exists
        if [ -d "$THEMES_DIR" ]; then
                preserve_component "$THEMES_DIR"
        else
                # Look for theme-related files elsewhere
                find "./frontend/client/src" -path "*theme*" -name "*.js" -o -name "*.ts" -o -name "*.json" | while read file; do
                        preserve_component "$file"
                done
        fi
}

# Function to preserve assets
preserve_assets() {
        echo "Preserving LibreChat assets..."

        # Define the source directory for assets
        ASSETS_DIR="./frontend/client/public"

        # Create assets directory in preservation directory
        mkdir -p "$PRESERVATION_DIR/assets"

        # Copy icons, images, and fonts
        find "$ASSETS_DIR" -name "*.svg" -o -name "*.png" -o -name "*.jpg" -o -name "*.jpeg" -o -name "*.gif" -o -name "*.ico" -o -name "*.woff" -o -name "*.woff2" -o -name "*.ttf" -o -name "*.eot" | while read file; do
                preserve_component "$file"
        done
}

# Function to create a README file
create_readme() {
        echo "Creating README file..."

        local readme="$PRESERVATION_DIR/README.md"

        echo "# LibreChat UI Components" >$readme
        echo "" >>$readme
        echo "This directory contains preserved UI components from LibreChat for potential future use in Atlas-Chat." >>$readme
        echo "" >>$readme
        echo "## Directory Structure" >>$readme
        echo "" >>$readme
        echo "- \`components/\`: UI components" >>$readme
        echo "- \`utils/\`: Utility functions" >>$readme
        echo "- \`hooks/\`: React hooks" >>$readme
        echo "- \`styles/\`: CSS and SCSS files" >>$readme
        echo "- \`themes/\`: Theme configurations" >>$readme
        echo "- \`assets/\`: Icons, images, and fonts" >>$readme
        echo "" >>$readme
        echo "## Usage" >>$readme
        echo "" >>$readme
        echo "These components can be used as references or directly imported into Atlas-Chat with appropriate modifications." >>$readme
        echo "" >>$readme
        echo "## Component Manifest" >>$readme
        echo "" >>$readme
        echo "See \`manifest.json\` for a complete list of preserved components." >>$readme
        echo "" >>$readme
        echo "## Preservation Date" >>$readme
        echo "" >>$readme
        echo "These components were preserved on $(date +%Y-%m-%d)." >>$readme

        echo "Created README file: $readme"
}

# Function to create a usage guide
create_usage_guide() {
        echo "Creating usage guide..."

        local guide="$PRESERVATION_DIR/USAGE_GUIDE.md"

        echo "# LibreChat UI Components Usage Guide" >$guide
        echo "" >>$guide
        echo "This guide provides instructions for using the preserved LibreChat UI components in Atlas-Chat." >>$guide
        echo "" >>$guide
        echo "## Integration Steps" >>$guide
        echo "" >>$guide
        echo "1. **Copy Components**: Copy the desired components to the appropriate directories in Atlas-Chat." >>$guide
        echo "2. **Update Imports**: Update import paths in the copied components." >>$guide
        echo "3. **Resolve Dependencies**: Install any missing dependencies." >>$guide
        echo "4. **Adapt to Atlas-Chat**: Modify the components to work with Atlas-Chat's state management and API." >>$guide
        echo "" >>$guide
        echo "## Component Categories" >>$guide
        echo "" >>$guide
        echo "### Chat Components" >>$guide
        echo "" >>$guide
        echo "These components handle the chat interface, including messages, input, and conversation management." >>$guide
        echo "" >>$guide
        echo "### UI Components" >>$guide
        echo "" >>$guide
        echo "These are general-purpose UI components like dropdowns, modals, and buttons." >>$guide
        echo "" >>$guide
        echo "### Settings Components" >>$guide
        echo "" >>$guide
        echo "These components handle user settings and preferences." >>$guide
        echo "" >>$guide
        echo "### Auth Components" >>$guide
        echo "" >>$guide
        echo "These components handle user authentication." >>$guide
        echo "" >>$guide
        echo "### Layout Components" >>$guide
        echo "" >>$guide
        echo "These components define the overall layout of the application." >>$guide
        echo "" >>$guide
        echo "## Styling" >>$guide
        echo "" >>$guide
        echo "The preserved styles use a combination of Tailwind CSS and custom CSS. To use these styles:" >>$guide
        echo "" >>$guide
        echo "1. Copy the relevant CSS/SCSS files to Atlas-Chat." >>$guide
        echo "2. Update the Tailwind configuration if necessary." >>$guide
        echo "3. Import the styles in the appropriate components." >>$guide
        echo "" >>$guide
        echo "## Theming" >>$guide
        echo "" >>$guide
        echo "The preserved themes can be used to implement a theme system in Atlas-Chat:" >>$guide
        echo "" >>$guide
        echo "1. Copy the theme configurations to Atlas-Chat." >>$guide
        echo "2. Implement a theme provider component." >>$guide
        echo "3. Use the theme values in your components." >>$guide
        echo "" >>$guide
        echo "## Best Practices" >>$guide
        echo "" >>$guide
        echo "- Test each component thoroughly after integration." >>$guide
        echo "- Keep track of any modifications made to the original components." >>$guide
        echo "- Consider creating a component library for reusable components." >>$guide
        echo "- Document any issues or limitations encountered during integration." >>$guide

        echo "Created usage guide: $guide"
}

# Function to create a component map
create_component_map() {
        echo "Creating component map..."

        local map="$PRESERVATION_DIR/COMPONENT_MAP.md"

        echo "# LibreChat UI Component Map" >$map
        echo "" >>$map
        echo "This map provides an overview of the preserved LibreChat UI components and their relationships." >>$map
        echo "" >>$map
        echo "## Component Hierarchy" >>$map
        echo "" >>$map
        echo "```" >>$map
        echo "App" >>$map
        echo "├── Layout" >>$map
        echo "│   ├── Header" >>$map
        echo "│   ├── Sidebar" >>$map
        echo "│   ├── Main" >>$map
        echo "│   └── Footer" >>$map
        echo "├── Chat" >>$map
        echo "│   ├── Conversation" >>$map
        echo "│   ├── Messages" >>$map
        echo "│   │   ├── ChatMessage" >>$map
        echo "│   │   ├── Markdown" >>$map
        echo "│   │   └── CodeBlock" >>$map
        echo "│   ├── Input" >>$map
        echo "│   └── ChatBar" >>$map
        echo "├── UI" >>$map
        echo "│   ├── Dropdown" >>$map
        echo "│   ├── Modal" >>$map
        echo "│   ├── Tooltip" >>$map
        echo "│   ├── Popover" >>$map
        echo "│   ├── Button" >>$map
        echo "│   ├── Card" >>$map
        echo "│   ├── Avatar" >>$map
        echo "│   └── Icons" >>$map
        echo "├── Settings" >>$map
        echo "│   ├── SettingsDialog" >>$map
        echo "│   ├── SettingsOption" >>$map
        echo "│   └── ThemeSelector" >>$map
        echo "└── Auth" >>$map
        echo "    ├── Login" >>$map
        echo "    ├── Register" >>$map
        echo "    └── ForgotPassword" >>$map
        echo "```" >>$map
        echo "" >>$map
        echo "## Component Dependencies" >>$map
        echo "" >>$map
        echo "- **Chat Components**: Depend on UI components and utility functions" >>$map
        echo "- **UI Components**: Mostly independent, some depend on utility functions" >>$map
        echo "- **Settings Components**: Depend on UI components and theme utilities" >>$map
        echo "- **Auth Components**: Depend on UI components and auth utilities" >>$map
        echo "- **Layout Components**: Depend on UI components and theme utilities" >>$map
        echo "" >>$map
        echo "## Utility Functions" >>$map
        echo "" >>$map
        echo "- **markdown**: Used by Markdown and CodeBlock components" >>$map
        echo "- **theme**: Used by ThemeSelector and various UI components" >>$map
        echo "- **storage**: Used by various components for local storage" >>$map
        echo "- **auth**: Used by Auth components" >>$map
        echo "- **chat**: Used by Chat components" >>$map
        echo "" >>$map
        echo "## Hooks" >>$map
        echo "" >>$map
        echo "- **useLocalStorage**: Used for persistent storage" >>$map
        echo "- **useMediaQuery**: Used for responsive design" >>$map
        echo "- **useDebounce**: Used for performance optimization" >>$map
        echo "- **useTheme**: Used for theme management" >>$map

        echo "Created component map: $map"
}

# Main execution
echo "Starting LibreChat UI preservation process..."

# Execute preservation functions
preserve_ui_components
preserve_styles
preserve_themes
preserve_assets

# Create documentation
create_manifest
create_readme
create_usage_guide
create_component_map

echo "LibreChat UI preservation process completed successfully."
echo "Preserved components are available in: $PRESERVATION_DIR"
