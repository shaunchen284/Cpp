//
// Created by lenovo on 2024/5/23.
//

#include "swap.h"
void swap(int x,int y){
    cout<<x<<endl;
    cout<<y<<endl;

    int temp = x;
    x = y;
    y = temp;
    cout<<x<<endl;
    cout<<y<<endl;
    return ;
}