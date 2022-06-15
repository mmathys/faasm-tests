cmake_minimum_required(VERSION 3.8.0)
project(faasm-func)

set(CMAKE_CXX_STANDARD 17)

set(CMAKE_EXPORT_COMPILE_COMMANDS ON)

set(FAASM_NATIVE_INSTALL "/usr/local/faasm/native")

SET(CMAKE_EXE_LINKER_FLAGS "${FAASM_EXE_LINKER_FLAGS} \
    -Xlinker --export=_faasm_zygote \
    -Xlinker --export=__heap_base \
    -Xlinker --export=__data_end \
    -Xlinker --export=__wasm_call_ctors \
    -Xlinker --max-memory=4294901760 \
    -Wl,-z,stack-size=4194304 -Wl, \
")

SET(CMAKE_EXECUTABLE_SUFFIX ".wasm")


# ----------------------
# Wasm build
# ----------------------

set(FAASM_FUNC_LIBS faasm c-printscan-long-double)

function(faasm_func_c func_name file_name)
    add_executable(${func_name} ${file_name})
    target_link_libraries(${func_name} ${FAASM_FUNC_LIBS})
endfunction(faasm_func_c)

function(faasm_func func_name file_name)
    add_executable(${func_name} ${file_name})
    target_link_libraries(${func_name} ${FAASM_FUNC_LIBS})
endfunction(faasm_func)

function(faasm_dynamic_func func_name file_name)
faasm_func(${func_name} ${file_name})

# These are the linker flags required for functions that will also do
# dynamic linking.
# We need to export all symbols to make them available to the
# dynamically loaded modules
set_target_properties(${func_name} PROPERTIES
    LINK_FLAGS "-Xlinker --export-all -Xlinker --no-gc-sections"
)

endfunction(faasm_dynamic_func)

set(FAASM_USER demo)

function(demo_func exec_name dir_path)
    faasm_func(${exec_name} ${dir_path})
    set(ALL_DEMO_FUNCS ${ALL_DEMO_FUNCS} ${exec_name} PARENT_SCOPE)
endfunction(demo_func)

function(demo_func_c exec_name dir_path)
    faasm_func_c(${exec_name} ${dir_path})
    set(ALL_DEMO_FUNCS ${ALL_DEMO_FUNCS} ${exec_name} PARENT_SCOPE)
endfunction(demo_func_c)

demo_func(hello hello.cpp)

if (CMAKE_SYSTEM_NAME STREQUAL "Wasm")
    demo_func(emscripten_check libs/emscripten_check.cpp)
    target_link_libraries(emscripten_check emscripten)
endif()

faasm_dynamic_func(dynlink libs/dynlink.cpp)
set(ALL_DEMO_FUNCS ${ALL_DEMO_FUNCS} dynlink)

# Custom target to group all the demo functions
add_custom_target(demo_all_funcs DEPENDS ${ALL_DEMO_FUNCS})
