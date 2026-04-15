LNode *GetElem(LinkList L, int i){
    LNode *p = L;
    int j = 0;
    while(p!=NULL && j<i){
        p = p->next;
        j++;
    }
    return p;
}