// SPDX-License-Identifier: GPL-2.0 OR BSD-3-Clause

#include "vmlinux.h"
#include <bpf/bpf_helpers.h>
#include <bpf/bpf_tracing.h>
#include <bpf/bpf_core_read.h>
#include "sched_common.h"

char LICENSE[] SEC("license") = "GPL";

unsigned long tgidpid = 0;
unsigned long cgid = 0;
unsigned long allret = 0;
unsigned long max_exec_slice = 0;


struct {
	__uint(type,BPF_MAP_TYPE_ARRAY);
        __type(key,int);
        __type(value, func_sched_item);
        __uint(max_entries,100);
} func_map SEC(".maps");


struct {
	__uint(type,BPF_MAP_TYPE_ARRAY);
        __type(key,int);
        __type(value, func_sched_execution);
        __uint(max_entries,100);
} execution_map SEC(".maps");



#define INVALID_RET ((unsigned long) -1L)

//#define debug(args...) bpf_printk(args)
#define debug(args...)
SEC("sched/cfs_entity_before")
int BPF_PROG(prio_less, int apred, int bpred, u64 avmtime, u64 bvmtime)
{	
	//in this policy, REAL > NORMAL > class 1 > class 2
    if(apred == bpred){
        return (s64)(avmtime - bvmtime) < 0;
    }else{
        if (apred > 0 || bpred > 0){
            func_sched_item *aresult;
            func_sched_item *bresult;
            unsigned long a_priority = 0;
            unsigned long b_priority = 0;
            aresult = bpf_map_lookup_elem(&func_map, &apred);
            bresult = bpf_map_lookup_elem(&func_map, &bpred);
            if (aresult){
                a_priority = aresult->p1;
            }
            if (bresult){
                b_priority = bresult->p1;
            }
            return (a_priority - b_priority) < 0;
            }
    }
	return 0;
}


SEC("sched/cfs__schedule")
int BPF_PROG(_schedule, struct task_struct *prev, struct task_struct *p, int check_pred)
{
	        
    int ret = 0;
	struct sched_entity *s;
	s = &prev->se;
	if(check_pred > 0){
		s64 diff_time = s->sum_exec_runtime - s->prev_sum_exec_runtime;
		func_sched_item *result;
		result = bpf_map_lookup_elem(&func_map, &check_pred);
		if (result){
			unsigned long bound = result->p2;		
			if(bound > diff_time){
				ret = 1;
			}else{
				ret = 0;
			}
        		if(!s->on_rq){
                		ret = 0;
        		}
		}
	}else{
		ret = 0;
	}
        return ret;
}

int Cal_threshold(int para1, int para2){
	return para1 + para2;
}