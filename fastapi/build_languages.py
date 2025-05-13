from tree_sitter import Language

# Build Python grammar
Language.build_library(
    'build/tree-sitter-python.so',
    ['vendor/tree-sitter-python']
)

# Build JavaScript grammar
Language.build_library(
    'build/tree-sitter-javascript.so',
    ['vendor/tree-sitter-javascript']
)

# Build Java grammar
Language.build_library(
    'build/tree-sitter-java.so',
    ['vendor/tree-sitter-java']
)

