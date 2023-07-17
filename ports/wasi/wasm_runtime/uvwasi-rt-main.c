/* Link this with wasm2c output and uvwasi runtime to build a standalone app */
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include "uvwasi.h"
#include "uvwasi-rt.h"

#define MODULE_NAME micropython
#include "micropython.wasm.h"

//force pre-processor expansion of m_name
#define __module_init(m_name) Z_## m_name ##_init_module()
#define module_init(m_name) __module_init(m_name)

#define __module_instantiate(m_name, instance_p, wasi_p) Z_## m_name ##_instantiate(instance_p, wasi_p)
#define module_instantiate(m_name ,instance_p, wasi_p) __module_instantiate(m_name ,instance_p, wasi_p)

#define __module_free(m_name, instance_p)  Z_## m_name ##_free(instance_p)
#define module_free(m_name, instance_p) __module_free(m_name, instance_p)

#define __module_start(m_name, instance_p) Z_ ## m_name ## Z__start(instance_p)
#define module_start(m_name, instance_p) __module_start(m_name, instance_p)


// TODO:snoopj:Python side should be able to make instances...
static Z_micropython_instance_t global_instance;
uvwasi_t global_uvwasi_state;
struct Z_wasi_snapshot_preview1_instance_t global_wasi_state = {
    .uvwasi = &global_uvwasi_state,
    .instance_memory = &global_instance.w2c_memory
};


u32 mp_do_str(const char* src)
{
    u32 len = strlen(src) + 1;  // 1 extra for the null terminator
    u32 addr = Z_micropythonZ_warehouse_addr(&global_instance);
    wasm_rt_memcpy(&global_instance.w2c_memory.data[addr], src, len);

    u32 result = Z_micropythonZ_do_str(&global_instance, addr, (u32)1 /* MP_PARSE_FILE_INPUT */);

    return result;
}


int main(int argc, const char** argv)
{
    uvwasi_options_t init_options;

    //pass in standard descriptors
    init_options.in = 0;
    init_options.out = 1;
    init_options.err = 2;
    init_options.fd_table_size = 3;

    //pass in args and environement
    extern const char ** environ;
    init_options.argc = argc;
    init_options.argv = argv;
    init_options.envp = (const char **) environ;

    //no sandboxing enforced, binary has access to everything user does
    init_options.preopenc = 2;
    init_options.preopens = calloc(2, sizeof(uvwasi_preopen_t));

    init_options.preopens[0].mapped_path = "/";
    init_options.preopens[0].real_path = "/";
    init_options.preopens[1].mapped_path = "./";
    init_options.preopens[1].real_path = ".";

    init_options.allocator = NULL;

    wasm_rt_init();
    uvwasi_errno_t ret = uvwasi_init(&global_uvwasi_state, &init_options);

    if (ret != UVWASI_ESUCCESS) {
        printf("uvwasi_init failed with error %d\n", ret);
        exit(1);
    }

    module_init(MODULE_NAME);
    module_instantiate(MODULE_NAME, &global_instance, (struct Z_wasi_snapshot_preview1_instance_t *) &global_wasi_state);
    module_start(MODULE_NAME, &global_instance);


// TODO: currently the global module is never freed, so that mp_do_str() can be called from Python
// In practice, this isn't a problem since the WASM module's lifetime is associated with its own process

//     module_free(MODULE_NAME, &global_instance);
//     uvwasi_destroy(&global_uvwasi_state);
//     wasm_rt_free();

    return 0;
}
