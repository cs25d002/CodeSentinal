from tree_sitter import Language
import os

# Make sure these paths exist
LIB_PATH = 'build/my-languages.so'
GRAMMAR_REPOS = ['vendor/tree-sitter-python']

# Create build directory if not present
os.makedirs('build', exist_ok=True)

# Build the language library
Language.build_library(
    # Store the compiled library
    LIB_PATH,
    # Include one or more grammars
    GRAMMAR_REPOS
)

print(f"✅ Built language library at {LIB_PATH}")
